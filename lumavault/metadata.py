"""Metadata extraction adapted from ComfyUI Image Browser v1.6.0.
Standalone: no ComfyUI imports or running server required.
"""

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

try:
    from PIL import Image, ExifTags
except ImportError:
    Image = None
    ExifTags = None

def _safe_str(value):
    if value is None:
        return ""
    if isinstance(value, bytes):
        try:
            return value.decode("utf-8", errors="ignore")
        except Exception:
            return f"<{len(value)} bytes>"
    return str(value)

def extract_metadata(image_path):
    """Extract metadata from image (PNG/JPEG/WEBP/etc)"""
    try:
        if not Image or not image_path.exists():
            return {}
        
        with Image.open(image_path) as img:
            metadata = {}
            
            # Extract PNG text chunks (ComfyUI stores workflow here)
            if hasattr(img, 'text'):
                for key, value in img.text.items():
                    metadata[key] = value
            
            # Also check PNG info dict
            if hasattr(img, 'info'):
                for key, value in img.info.items():
                    if key not in metadata:
                        metadata[key] = value

            # EXIF (JPEG/WEBP/etc)
            exif_data = {}
            try:
                if hasattr(img, "_getexif") and img._getexif():
                    for tag, val in img._getexif().items():
                        name = ExifTags.TAGS.get(tag, str(tag)) if Image else str(tag)
                        exif_data[name] = val
            except Exception:
                pass
            if exif_data:
                metadata["EXIF"] = exif_data

            # XMP (if present)
            if "XML:com.adobe.xmp" in metadata:
                metadata["XMP"] = metadata.get("XML:com.adobe.xmp")
            elif "xmp" in metadata:
                metadata["XMP"] = metadata.get("xmp")

            # If ICC profile exists, include a summary only
            if "icc_profile" in metadata:
                icc = metadata.get("icc_profile")
                metadata["ICC Profile"] = f"<{len(icc)} bytes>" if isinstance(icc, (bytes, bytearray)) else _safe_str(icc)
            
            # Try to decode 'prompt' and 'workflow' if they are JSON strings
            for key in ['prompt', 'workflow']:
                if key in metadata and isinstance(metadata[key], str):
                    try:
                        metadata[key] = json.loads(metadata[key])
                    except:
                        pass
            
            return metadata
    except Exception as e:
        print(f"Error extracting metadata from {image_path}: {e}")
        return {}

def _validate_and_get_workflow(json_string):
    try:
        data = json.loads(json_string)
        workflow_data = data.get('workflow', data.get('prompt', data))

        if isinstance(workflow_data, dict):
            if 'nodes' in workflow_data:
                return workflow_data, 'ui'

            is_api = False
            for _, value in workflow_data.items():
                if isinstance(value, dict) and 'class_type' in value:
                    is_api = True
                    break
            if is_api:
                return workflow_data, 'api'
    except Exception:
        pass
    return None, None

def _scan_bytes_for_workflow(content_bytes):
    """
    Yield valid JSON object strings found in a binary stream by brace matching.
    """
    try:
        stream_str = content_bytes.decode('utf-8', errors='ignore')
    except Exception:
        return

    start_pos = 0
    while True:
        first_brace = stream_str.find('{', start_pos)
        if first_brace == -1:
            break

        open_braces = 0
        start_index = first_brace

        for i in range(start_index, len(stream_str)):
            char = stream_str[i]
            if char == '{':
                open_braces += 1
            elif char == '}':
                open_braces -= 1

            if open_braces == 0:
                candidate = stream_str[start_index:i + 1]
                try:
                    json.loads(candidate)
                    yield candidate
                except Exception:
                    pass
                start_pos = i + 1
                break
        else:
            break

def extract_workflow_from_file(file_path):
    """
    Extract workflow payload from image/video/audio files.
    Returns (workflow_dict_or_none, 'ui'|'api'|None).
    """
    found = {}

    def analyze_json(json_str):
        wf, wf_type = _validate_and_get_workflow(json_str)
        if wf and wf_type and wf_type not in found:
            found[wf_type] = wf

    ext_lower = str(file_path).lower()
    is_media = ext_lower.endswith(('.mp4', '.mkv', '.webm', '.mov', '.avi', '.mp3', '.wav', '.ogg', '.flac', '.m4a', '.aac'))

    # Video/audio metadata tags via ffprobe (primary path for many encoded files)
    if is_media:
        ffprobe_bin = os.environ.get('FFPROBE_PATH') or shutil.which('ffprobe')
        if ffprobe_bin:
            try:
                cmd = [ffprobe_bin, '-v', 'quiet', '-print_format', 'json', '-show_format', str(file_path)]
                creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='ignore',
                    check=True,
                    creationflags=creationflags
                )
                ff_data = json.loads(result.stdout)
                tags = ff_data.get('format', {}).get('tags', {})
                if isinstance(tags, dict):
                    for value in tags.values():
                        if not isinstance(value, str):
                            continue
                        if value.strip().startswith('{'):
                            analyze_json(value)
                        elif '{' in value:
                            for json_str in _scan_bytes_for_workflow(value.encode('utf-8', errors='ignore')):
                                analyze_json(json_str)
            except Exception:
                pass

    # Fast image metadata path (PNG/JPG/WEBP text chunks, EXIF)
    if Image:
        try:
            with Image.open(file_path) as img:
                for key in ['workflow', 'prompt']:
                    value = img.info.get(key)
                    if isinstance(value, str) and value.strip().startswith('{'):
                        analyze_json(value)

                exif_data = img.info.get('exif')
                if isinstance(exif_data, bytes):
                    for json_str in _scan_bytes_for_workflow(exif_data):
                        analyze_json(json_str)
        except Exception:
            pass

    # Ultimate fallback: scan raw bytes (works for video/audio metadata blobs too)
    if not found:
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            for json_str in _scan_bytes_for_workflow(content):
                analyze_json(json_str)
                if 'ui' in found and 'api' in found:
                    break
        except Exception:
            pass

    if 'ui' in found:
        return found['ui'], 'ui'
    if 'api' in found:
        return found['api'], 'api'
    return None, None

def _parse_parameters_text(params_text, parsed):
    if not params_text or not isinstance(params_text, str):
        return
    text = params_text.strip()
    if not text:
        return

    # Positive prompt (explicit label, if present)
    pos_match = re.search(
        r'(?:^|\n)Positive prompt:\s*(.+?)(?=\n(?:Negative prompt:|Steps:|Seed:|Sampler:|CFG(?: scale)?:|CfgScale:|Size:|Model:|Scheduler:|$))',
        text,
        re.DOTALL,
    )
    if pos_match and not parsed['prompt']:
        parsed['prompt'] = pos_match.group(1).strip()

    # Fallback: extract unlabeled positive prompt block (common in A1111/Forge parameters)
    if not parsed['prompt']:
        marker_match = re.search(
            r'(?m)^\s*(Negative prompt:|Steps:|Seed:|Sampler:|CFG(?: scale)?:|CfgScale:|Size:|Model:|Scheduler:)',
            text,
        )
        prompt_block = text[:marker_match.start()] if marker_match else text
        prompt_block = prompt_block.strip()
        first_line = prompt_block.split('\n', 1)[0].strip() if prompt_block else ''
        if prompt_block and not re.search(
            r'^(Steps:|Seed:|Sampler:|CFG(?: scale)?:|CfgScale:|Size:|Model:|Scheduler:)',
            first_line,
        ):
            parsed['prompt'] = prompt_block

    # Negative prompt
    neg_match = re.search(
        r'(?:^|\n)Negative prompt:\s*(.+?)(?=\n(?:Steps:|Seed:|Sampler:|CFG(?: scale)?:|CfgScale:|Size:|Model:|Scheduler:|$))',
        text,
        re.DOTALL,
    )
    if neg_match and not parsed['negative_prompt']:
        parsed['negative_prompt'] = neg_match.group(1).strip()

    # Standard parameters
    steps_match = re.search(r'Steps:\s*(\d+)', text)
    if steps_match and not parsed['steps']:
        parsed['steps'] = int(steps_match.group(1))

    sampler_match = re.search(r'Sampler:\s*([^,\n]+)', text)
    if sampler_match and not parsed['sampler']:
        parsed['sampler'] = sampler_match.group(1).strip()

    scheduler_match = re.search(r'Scheduler:\s*([^,\n]+)', text)
    if scheduler_match and not parsed['scheduler']:
        parsed['scheduler'] = scheduler_match.group(1).strip()

    cfg_match = re.search(r'CFG scale:\s*([\d.]+)', text) or re.search(r'CfgScale:\s*([\d.]+)', text)
    if cfg_match and not parsed['cfg']:
        parsed['cfg'] = float(cfg_match.group(1))

    seed_match = re.search(r'Seed:\s*(\d+)', text)
    if seed_match and not parsed['seed']:
        parsed['seed'] = int(seed_match.group(1))

    size_match = re.search(r'Size:\s*(\d+)x(\d+)', text)
    if size_match and not parsed['width'] and not parsed['height']:
        parsed['width'] = int(size_match.group(1))
        parsed['height'] = int(size_match.group(2))

    model_match = re.search(r'Model:\s*([^,\n]+)', text)
    if model_match and not parsed['model']:
        parsed['model'] = model_match.group(1).strip()

    # Extra fields
    extra_fields = {
        "Model hash": r'Model hash:\s*([^,\n]+)',
        "VAE": r'VAE:\s*([^,\n]+)',
        "VAE hash": r'VAE hash:\s*([^,\n]+)',
        "Clip skip": r'Clip skip:\s*([^,\n]+)',
        "Denoising strength": r'Denoising strength:\s*([\d.]+)',
        "Hires steps": r'Hires steps:\s*([^,\n]+)',
        "Hires upscale": r'Hires upscale:\s*([^,\n]+)',
        "Hires resize": r'Hires resize:\s*([^,\n]+)',
        "Refiner": r'Refiner:\s*([^,\n]+)',
        "Refiner switch": r'Refiner switch:\s*([^,\n]+)',
        "Version": r'Version:\s*([^,\n]+)',
        "RNG": r'RNG:\s*([^,\n]+)'
    }
    for label, pattern in extra_fields.items():
        m = re.search(pattern, text)
        if m:
            parsed['extras'][label] = m.group(1).strip()

    # Extract LoRAs from prompt text
    if text:
        lora_tags = re.findall(r'<lora:([^:>]+):([\d.]+)>', text)
        for lora_name, strength in lora_tags:
            lora_name = lora_name.strip()
            if lora_name and lora_name not in ['None', '', 'ComfyUI']:
                if not any(l['name'] == lora_name for l in parsed['loras']):
                    parsed['loras'].append({
                        'name': lora_name,
                        'strength_model': float(strength),
                        'strength_clip': float(strength)
                    })

def _sanitize_prompt_text(prompt_text):
    """Remove inline LoRA tags from display prompt while preserving line structure."""
    if not isinstance(prompt_text, str):
        return prompt_text

    cleaned = re.sub(r'[ \t]*<lora:[^>]+>[ \t]*', ' ', prompt_text, flags=re.IGNORECASE)
    out_lines = []
    for line in cleaned.splitlines():
        line = re.sub(r'[ \t]+', ' ', line).strip()
        line = re.sub(r'\s+,', ',', line)
        line = re.sub(r',\s*,', ',', line)
        if line:
            out_lines.append(line)
    return '\n'.join(out_lines).strip()


def _decode_json_maybe(value):
    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception:
            return value
    return value


def _is_link_ref(value):
    return isinstance(value, (list, tuple)) and len(value) >= 1 and isinstance(value[0], (str, int))


def _node_title(node):
    if not isinstance(node, dict):
        return ''
    meta = node.get('_meta') or {}
    if not isinstance(meta, dict):
        meta = {}
    return str(node.get('title') or meta.get('title') or '')


def _node_type(node):
    if not isinstance(node, dict):
        return ''
    return str(node.get('class_type') or node.get('type') or '')


def _iter_ui_workflow_nodes(workflow_data):
    """Yield (node, id_prefix, subgraph_name) for top-level and definitions.subgraphs UI nodes."""
    if not isinstance(workflow_data, dict):
        return

    for node in workflow_data.get('nodes', []) or []:
        if isinstance(node, dict):
            yield node, '', None

    definitions = workflow_data.get('definitions')
    if not isinstance(definitions, dict):
        return

    for subgraph in definitions.get('subgraphs', []) or []:
        if not isinstance(subgraph, dict):
            continue
        subgraph_id = _safe_str(subgraph.get('id') or subgraph.get('name') or 'subgraph')
        subgraph_name = _safe_str(subgraph.get('name') or subgraph_id)
        for node in subgraph.get('nodes', []) or []:
            if isinstance(node, dict):
                yield node, f'{subgraph_id}:', subgraph_name


def _coerce_number(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, str):
        text = value.strip()
        if re.fullmatch(r'-?\d+', text):
            return int(text)
        if re.fullmatch(r'-?\d+\.\d+', text):
            return float(text)
    return None


def _resolve_api_value(prompt_graph, value, preferred_names=None, want='text', visited=None):
    """Resolve a ComfyUI API graph input, following links through text/prompt/string/size helper nodes."""
    if visited is None:
        visited = set()
    preferred_names = preferred_names or []

    if _is_link_ref(value):
        node_key = str(value[0])
        if node_key in visited:
            return None
        visited.add(node_key)

        # Runtime text-generator outputs are links, not literal API inputs. Some
        # workflows preserve the resolved output in a ShowText node (text_0,
        # text_1, ...). Recover that snapshot before inspecting model settings
        # such as model_name, which are not prompts.
        if want == 'text':
            for consumer in prompt_graph.values():
                if not isinstance(consumer, dict) or 'showtext' not in _node_type(consumer).lower():
                    continue
                consumer_inputs = consumer.get('inputs', {})
                if not isinstance(consumer_inputs, dict):
                    continue
                links_to_target = any(
                    _is_link_ref(input_value) and str(input_value[0]) == node_key
                    for input_value in consumer_inputs.values()
                )
                if not links_to_target:
                    continue
                for snapshot_name in sorted(name for name in consumer_inputs if str(name).startswith('text_')):
                    snapshot = consumer_inputs.get(snapshot_name)
                    if isinstance(snapshot, str) and snapshot.strip():
                        return snapshot.strip()

        ref_node = prompt_graph.get(node_key)
        if not isinstance(ref_node, dict):
            return None
        return _extract_api_node_value(prompt_graph, ref_node, preferred_names, want, visited)

    if want == 'number':
        return _coerce_number(value)
    if isinstance(value, str):
        return value.strip()
    if value is not None and want != 'text':
        return value
    return None


def _extract_api_node_value(prompt_graph, node, preferred_names=None, want='text', visited=None):
    preferred_names = preferred_names or []
    visited = visited or set()
    inputs = node.get('inputs', {}) if isinstance(node, dict) else {}
    if not isinstance(inputs, dict):
        return None

    node_type_l = _node_type(node).lower()
    if want == 'text' and 'stringconcatenate' in node_type_l:
        delimiter = inputs.get('delimiter', '')
        if not isinstance(delimiter, str):
            delimiter = ''
        parts = []
        for key in sorted([k for k in inputs if str(k).startswith('string_')]):
            part = _resolve_api_value(prompt_graph, inputs.get(key), want='text', visited=set(visited))
            if isinstance(part, str) and part.strip():
                parts.append(part.strip())
        if parts:
            return delimiter.join(parts).strip()

    for name in preferred_names:
        if name in inputs:
            resolved = _resolve_api_value(prompt_graph, inputs.get(name), preferred_names, want, set(visited))
            if resolved not in (None, ''):
                return resolved
    if want == 'text' and any(name in inputs for name in preferred_names):
        # A preferred text/prompt field exists but is empty. Do not fall through into
        # unrelated inputs such as clip/model/vae links and mistake filenames for prompts.
        return None

    if want == 'number':
        for name in ['width', 'height', 'steps', 'cfg', 'seed', 'value', 'number', 'int', 'float']:
            if name in inputs:
                resolved = _resolve_api_value(prompt_graph, inputs.get(name), preferred_names, want, set(visited))
                if resolved is not None:
                    return resolved
        for value in inputs.values():
            resolved = _resolve_api_value(prompt_graph, value, preferred_names, want, set(visited))
            if resolved is not None:
                return resolved
        return None

    for name in ['text', 'prompt', 'positive', 'negative', 'string', 'string_a', 'value', 'name']:
        if name in inputs:
            resolved = _resolve_api_value(prompt_graph, inputs.get(name), preferred_names, want, set(visited))
            if isinstance(resolved, str) and resolved.strip():
                return resolved.strip()

    for value in inputs.values():
        resolved = _resolve_api_value(prompt_graph, value, preferred_names, want, set(visited))
        if isinstance(resolved, str) and resolved.strip():
            return resolved.strip()
    return None


def _add_lora(parsed, name, strength_model=1.0, strength_clip=None):
    if not name:
        return
    lora_name = str(name).strip()
    if lora_name in ['None', '', 'ComfyUI']:
        return
    if any(l['name'] == lora_name for l in parsed['loras']):
        return
    if strength_clip is None:
        strength_clip = strength_model
    parsed['loras'].append({
        'name': lora_name,
        'strength_model': strength_model,
        'strength_clip': strength_clip,
    })


def parse_comfy_metadata(metadata):
    """Parse ComfyUI/SD metadata with broad heuristics"""
    parsed = {
        'prompt': None, 
        'negative_prompt': None, 
        'seed': None,
        'steps': None, 
        'cfg': None, 
        'sampler': None,
        'scheduler': None, 
        'model': None, 
        'loras': [],
        'width': None, 
        'height': None,
        'extras': {}
    }
    

    try:
        # Try any known text-like fields first
        negative_prompt_keys = {'Negative prompt', 'negative_prompt', 'negativePrompt'}
        for key in [
            'parameters',
            'Comment',
            'Description',
            'UserComment',
            'ImageDescription',
            'Software',
            'Prompt',
            'prompt',
            'Negative prompt',
            'negative_prompt',
            'negativePrompt',
            'notes',
        ]:
            if key in metadata and isinstance(metadata[key], str):
                if key in negative_prompt_keys and not parsed['negative_prompt']:
                    parsed['negative_prompt'] = metadata[key].strip()
                    continue
                _parse_parameters_text(metadata[key], parsed)

        # If there is EXIF, scan for prompt-like text
        exif = metadata.get('EXIF')
        if isinstance(exif, dict):
            for k, v in exif.items():
                if isinstance(v, str) and any(x in v for x in ['Steps:', 'Sampler:', 'Negative prompt:', 'CFG']):
                    _parse_parameters_text(v, parsed)

        # First check if there's a 'parameters' field (Automatic1111/Forge/WebUI format)
        if 'parameters' in metadata:
            params_text = metadata['parameters']
            if isinstance(params_text, str):
                lines = params_text.split('\n')
                full_text = '\n'.join(lines[1:]) if len(lines) > 1 else ''

                # Also extract from Lora hashes field
                lora_match = re.search(r'Lora hashes:\s*"([^"]+)"', full_text)
                if lora_match:
                    lora_text = lora_match.group(1)
                    lora_pairs = lora_text.split(',')
                    for pair in lora_pairs:
                        if ':' in pair:
                            lora_name = pair.split(':')[0].strip()
                            # Only add valid LoRA names and avoid duplicates
                            if lora_name and lora_name not in ['None', '', 'ComfyUI']:
                                if not any(l['name'] == lora_name for l in parsed['loras']):
                                    # Try to extract strength from prompt
                                    strength_match = re.search(rf'<lora:{re.escape(lora_name)}:([\d.]+)>', parsed['prompt'] or '')
                                    strength = float(strength_match.group(1)) if strength_match else 1.0
                                    
                                    parsed['loras'].append({
                                        'name': lora_name,
                                        'strength_model': strength,
                                        'strength_clip': strength
                                    })
        
        # ComfyUI UI workflow format. Newer ComfyUI can keep important nodes inside
        # workflow.definitions.subgraphs, so iterate both top-level and subgraph nodes.
        workflow = _decode_json_maybe(metadata.get('workflow', {}))
        if isinstance(workflow, dict):
            for node, _id_prefix, _subgraph_name in _iter_ui_workflow_nodes(workflow):
                node_type = _node_type(node)
                node_type_l = node_type.lower()
                widgets = node.get('widgets_values', [])
                inputs = node.get('inputs', {})
                title = _node_title(node).lower()

                # Extract prompts from core and custom text-encode/prompt nodes.
                if any(kw in node_type_l for kw in ['cliptextencode', 'textencode', 'prompttext']):
                    text = widgets[0] if widgets and isinstance(widgets[0], str) else None
                    if not text and isinstance(inputs, dict):
                        text = inputs.get('text') or inputs.get('prompt')
                    if text:
                        is_negative = any(word in title for word in ['negative', 'neg'])
                        if is_negative and not parsed['negative_prompt']:
                            parsed['negative_prompt'] = text
                        elif not is_negative and not parsed['prompt']:
                            parsed['prompt'] = text

                # KSamplerSelect is only a sampler-name picker; treating its first
                # widget as a seed corrupts the details panel (for example seed="lcm").
                if 'ksampler' in node_type_l and 'select' not in node_type_l:
                    if not parsed['seed']:
                        parsed['seed'] = widgets[0] if widgets else (inputs.get('seed') if isinstance(inputs, dict) else None)
                    if not parsed['steps']:
                        parsed['steps'] = widgets[1] if len(widgets) > 1 else (inputs.get('steps') if isinstance(inputs, dict) else None)
                    if not parsed['cfg']:
                        parsed['cfg'] = widgets[2] if len(widgets) > 2 else (inputs.get('cfg') if isinstance(inputs, dict) else None)
                    if not parsed['sampler']:
                        parsed['sampler'] = widgets[3] if len(widgets) > 3 else (inputs.get('sampler_name') if isinstance(inputs, dict) else None)
                    if not parsed['scheduler']:
                        parsed['scheduler'] = widgets[4] if len(widgets) > 4 else (inputs.get('scheduler') if isinstance(inputs, dict) else None)

                # Extract model/checkpoint names.
                if any(kw in node_type_l for kw in ['checkpointloader', 'unetloader', 'modelloader']):
                    if not parsed['model']:
                        parsed['model'] = widgets[0] if widgets else None
                        if not parsed['model'] and isinstance(inputs, dict):
                            for key in ['ckpt_name', 'unet_name', 'model_name', 'name']:
                                if inputs.get(key):
                                    parsed['model'] = inputs.get(key)
                                    break

                # Extract LoRAs from LoRA Manager, standard loaders, stackers, and custom loaders.
                if any(kw in node_type_l for kw in ['lora', 'loraloader', 'lora stacker', 'lora_stack']):
                    try:
                        if widgets and isinstance(widgets[0], list):
                            for lora_obj in widgets[0]:
                                if isinstance(lora_obj, dict) and lora_obj.get('active', True):
                                    _add_lora(
                                        parsed,
                                        lora_obj.get('name'),
                                        lora_obj.get('strength', 1.0),
                                        lora_obj.get('clipStrength', lora_obj.get('strength', 1.0)),
                                    )
                        else:
                            lora_name = widgets[0] if widgets else None
                            strength_model = widgets[1] if len(widgets) > 1 else 1.0
                            strength_clip = widgets[2] if len(widgets) > 2 else strength_model
                            if isinstance(inputs, dict):
                                lora_name = lora_name or inputs.get('lora_name') or inputs.get('name')
                                strength_model = inputs.get('strength_model', inputs.get('lora_strength', inputs.get('strength', strength_model)))
                                strength_clip = inputs.get('strength_clip', inputs.get('clip_strength', inputs.get('clipStrength', strength_model)))
                            _add_lora(parsed, lora_name, strength_model, strength_clip)
                    except Exception as e:
                        print(f"Error parsing LoRAs from node {node_type}: {e}")

                # Extract dimensions.
                if 'emptylatentimage' in node_type_l or ('latent' in node_type_l and isinstance(inputs, dict) and 'width' in inputs and 'height' in inputs):
                    if not parsed['width']:
                        parsed['width'] = widgets[0] if widgets else inputs.get('width')
                    if not parsed['height']:
                        parsed['height'] = widgets[1] if len(widgets) > 1 else inputs.get('height')

        # Parse API prompt graph JSON (ComfyUI default Save Image metadata). This is the
        # most reliable source for images saved by core SaveImage and most custom save nodes.
        prompt_graph = _decode_json_maybe(metadata.get('prompt'))
        if isinstance(prompt_graph, dict):
            text_candidates = []
            api_negative_input_seen = False
            for _, node in prompt_graph.items():
                if not isinstance(node, dict):
                    continue
                node_type = _node_type(node)
                node_type_l = node_type.lower()
                title_l = _node_title(node).lower()
                node_inputs = node.get('inputs', {})
                if not isinstance(node_inputs, dict):
                    continue

                is_sampling_node = (
                    ('ksampler' in node_type_l and 'select' not in node_type_l)
                    or 'samplercustom' in node_type_l
                )
                if is_sampling_node:
                    # Prefer the API prompt graph over the UI workflow for sampler settings;
                    # UI widgets include control widgets (for example randomize/fixed) that
                    # shifted position in recent ComfyUI versions.
                    seed_value = node_inputs.get('seed', node_inputs.get('noise_seed'))
                    if seed_value is not None:
                        parsed['seed'] = seed_value
                    if node_inputs.get('steps') is not None:
                        parsed['steps'] = node_inputs.get('steps')
                    if node_inputs.get('cfg') is not None:
                        parsed['cfg'] = node_inputs.get('cfg')
                    if node_inputs.get('sampler_name') is not None:
                        parsed['sampler'] = node_inputs.get('sampler_name')
                    if node_inputs.get('scheduler') is not None:
                        parsed['scheduler'] = node_inputs.get('scheduler')

                    positive_text = _resolve_api_value(prompt_graph, node_inputs.get('positive'), ['text', 'prompt', 'positive', 'string_a', 'string'], 'text')
                    if positive_text:
                        parsed['prompt'] = positive_text
                    if 'negative' in node_inputs:
                        api_negative_input_seen = True
                    negative_text = _resolve_api_value(prompt_graph, node_inputs.get('negative'), ['text', 'prompt', 'negative', 'string_a', 'string'], 'text')
                    if negative_text:
                        parsed['negative_prompt'] = negative_text
                    elif 'negative' in node_inputs:
                        # The API graph explicitly says the negative input is empty. Do not keep
                        # stale/wrong text guessed from UI widgets (recent ComfyUI widgets moved).
                        parsed['negative_prompt'] = None

                # Newer/custom graphs can split sampling into SamplerCustom,
                # KSamplerSelect, and BasicScheduler nodes.
                if 'ksamplerselect' in node_type_l and node_inputs.get('sampler_name') is not None:
                    parsed['sampler'] = node_inputs.get('sampler_name')
                if 'scheduler' in node_type_l:
                    if node_inputs.get('steps') is not None:
                        parsed['steps'] = node_inputs.get('steps')
                    if node_inputs.get('scheduler') is not None:
                        parsed['scheduler'] = node_inputs.get('scheduler')

                if any(key in node_inputs for key in ['ckpt_name', 'unet_name', 'model_name']) or any(kw in node_type_l for kw in ['checkpointloader', 'unetloader', 'modelloader', 'ditloader']):
                    # Checkpoint/UNet names are the generation model. A generic
                    # model_name on a captioner or VLM helper must not overwrite it.
                    primary_model = node_inputs.get('ckpt_name') or node_inputs.get('unet_name')
                    if isinstance(primary_model, str) and primary_model.strip():
                        parsed['model'] = primary_model.strip()
                    elif not parsed['model']:
                        for key in ['model_name', 'name']:
                            if isinstance(node_inputs.get(key), str) and node_inputs.get(key).strip():
                                parsed['model'] = node_inputs.get(key).strip()
                                break

                if any(kw in node_type_l for kw in ['lora', 'loraloader', 'lora_stack', 'lora stacker']):
                    lora_name = _resolve_api_value(prompt_graph, node_inputs.get('lora_name') or node_inputs.get('name'), ['lora_name', 'name'], 'text')
                    strength_model = node_inputs.get('strength_model', node_inputs.get('lora_strength', node_inputs.get('strength', 1.0)))
                    strength_clip = node_inputs.get('strength_clip', node_inputs.get('clip_strength', node_inputs.get('clipStrength', strength_model)))
                    _add_lora(parsed, lora_name, strength_model, strength_clip)

                if 'emptylatentimage' in node_type_l or ('latent' in node_type_l and 'width' in node_inputs and 'height' in node_inputs):
                    width_value = _resolve_api_value(prompt_graph, node_inputs.get('width'), ['width'], 'number')
                    height_value = _resolve_api_value(prompt_graph, node_inputs.get('height'), ['height'], 'number')
                    if width_value is not None:
                        parsed['width'] = width_value
                    if height_value is not None:
                        parsed['height'] = height_value

                if any(kw in node_type_l for kw in ['cliptextencode', 'textencode', 'conditioning', 'prompt']):
                    text = _extract_api_node_value(prompt_graph, node, ['text', 'prompt', 'string_a', 'string'], 'text')
                    if isinstance(text, str) and text.strip():
                        text_candidates.append((text.strip(), title_l))

            if not parsed['negative_prompt'] and not api_negative_input_seen:
                for text, title in text_candidates:
                    if any(word in title for word in ['negative', 'neg']):
                        parsed['negative_prompt'] = text
                        break

            if not parsed['prompt']:
                for text, title in text_candidates:
                    if not any(word in title for word in ['negative', 'neg']):
                        parsed['prompt'] = text
                        break

            # Do not invent a negative prompt from arbitrary extra text nodes. If a
            # workflow has a real negative prompt, it is either linked from the sampler
            # negative input or explicitly titled negative/neg above.
            if text_candidates and not parsed['prompt']:
                for text, _ in text_candidates:
                    parsed['prompt'] = text
                    break
    
    except Exception as e:
        print(f"Error parsing metadata: {e}")
        import traceback
        traceback.print_exc()

    # Final normalization: prompt display should not duplicate LoRA entries.
    parsed['prompt'] = _sanitize_prompt_text(parsed.get('prompt'))
    parsed['negative_prompt'] = _sanitize_prompt_text(parsed.get('negative_prompt'))

    if parsed.get('prompt') and parsed.get('negative_prompt') == parsed.get('prompt'):
        # Some workflows/models have no real negative prompt but the default ComfyUI
        # SaveImage API graph still routes the same conditioning/text to positive and
        # negative. Showing the same block twice is misleading; treat exact duplicates
        # as an absent negative prompt.
        parsed['negative_prompt'] = None

    return parsed

def flatten_metadata(metadata):
    flat = {}
    for key, value in metadata.items():
        if key == 'workflow':
            continue
        if isinstance(value, dict):
            for k2, v2 in value.items():
                flat[f"{key}.{k2}"] = _safe_str(v2)
        else:
            flat[key] = _safe_str(value)
    return flat

def _normalize_node_params_from_ui_node(node):
    params = []

    inputs = node.get('inputs', {})
    if isinstance(inputs, list):
        for idx, item in enumerate(inputs):
            if isinstance(item, dict):
                name = item.get('name') or f"input_{idx + 1}"
                value = item.get('widget', item.get('value', item.get('link')))
                params.append({'name': str(name), 'value': _safe_str(value)})
    elif isinstance(inputs, dict):
        for name, value in inputs.items():
            params.append({'name': str(name), 'value': _safe_str(value)})

    widgets = node.get('widgets_values', [])
    if isinstance(widgets, list):
        for idx, value in enumerate(widgets):
            params.append({'name': f"widget_{idx + 1}", 'value': _safe_str(value)})

    return params

def extract_workflow_nodes(metadata):
    """Extract workflow nodes for sidebar node inspector (UI and API workflow formats)."""
    workflow_data = metadata.get('workflow')
    prompt_data = metadata.get('prompt')
    source = workflow_data if workflow_data is not None else prompt_data

    if isinstance(source, str):
        try:
            source = json.loads(source)
        except Exception:
            return []

    nodes_out = []

    # UI format: {"nodes":[...], "definitions":{"subgraphs":[...]}}
    if isinstance(source, dict) and isinstance(source.get('nodes'), list):
        for node, id_prefix, subgraph_name in _iter_ui_workflow_nodes(source):
            if not isinstance(node, dict):
                continue
            if node.get('mode', 0) != 0:
                continue
            node_id = node.get('id', 'N/A')
            node_type = node.get('type') or node.get('class_type') or 'Unknown'
            params = _normalize_node_params_from_ui_node(node)
            if subgraph_name:
                params.insert(0, {'name': 'subgraph', 'value': subgraph_name})
            nodes_out.append({
                'id': f"{id_prefix}{_safe_str(node_id)}",
                'type': _safe_str(node_type),
                'params': params
            })
    # API format: {"3":{"class_type":"KSampler","inputs":{...}}, ...}
    elif isinstance(source, dict):
        for node_id, node in source.items():
            if not isinstance(node, dict) or 'class_type' not in node:
                continue
            params = []
            inputs = node.get('inputs', {})
            if isinstance(inputs, dict):
                for name, value in inputs.items():
                    params.append({'name': str(name), 'value': _safe_str(value)})
            nodes_out.append({
                'id': _safe_str(node_id),
                'type': _safe_str(node.get('class_type', 'Unknown')),
                'params': params
            })

    def _sort_key(item):
        node_id = item.get('id', '')
        try:
            return (0, int(node_id))
        except Exception:
            return (1, str(node_id))

    nodes_out.sort(key=_sort_key)
    return nodes_out

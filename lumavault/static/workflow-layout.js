(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.LumaVaultWorkflowLayout = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  const NODE_WIDTH = 264;
  const COLUMN_GAP = 96;
  const ROW_GAP = 42;
  const MAX_COLUMN_HEIGHT = 1100;
  const SCENE_PADDING = 64;
  const GROUP_PADDING_X = 54;
  const GROUP_PADDING_TOP = 76;
  const GROUP_PADDING_BOTTOM = 50;
  const GROUP_GAP = 110;

  function numberAt(value, index, fallback = 0) {
    const number = Number(Array.isArray(value) ? value[index] : undefined);
    return Number.isFinite(number) ? number : fallback;
  }

  function compactNodeHeight(node) {
    const inputs = Array.isArray(node.inputs) ? node.inputs.length : 0;
    const outputs = Array.isArray(node.outputs) ? node.outputs.length : 0;
    const params = Array.isArray(node.params) ? node.params : [];
    const portHeight = Math.max(inputs, outputs) * 22;
    const parameterHeight = params.length
      ? 14 + params.reduce((height, param) => height + (param?.multiline ? 74 : 22), 0)
      : 0;
    return Math.max(82, 58 + portHeight + parameterHeight);
  }

  function stableNodeOrder(left, right) {
    const yDifference = numberAt(left.position, 1) - numberAt(right.position, 1);
    if (yDifference) return yDifference;
    const xDifference = numberAt(left.position, 0) - numberAt(right.position, 0);
    if (xDifference) return xDifference;
    return String(left.id).localeCompare(String(right.id), undefined, { numeric: true });
  }

  function layoutScope(nodes, links, originX, originY) {
    if (!nodes.length) return { width: 0, height: 0 };
    const byId = new Map(nodes.map(node => [String(node.id), node]));
    const incoming = new Map(nodes.map(node => [String(node.id), 0]));
    const outgoing = new Map(nodes.map(node => [String(node.id), []]));

    for (const link of links) {
      const fromId = String(link?.from_node);
      const toId = String(link?.to_node);
      if (fromId === toId || !byId.has(fromId) || !byId.has(toId)) continue;
      outgoing.get(fromId).push(toId);
      incoming.set(toId, incoming.get(toId) + 1);
    }

    const depths = new Map(nodes.map(node => [String(node.id), 0]));
    const queue = nodes.filter(node => incoming.get(String(node.id)) === 0).sort(stableNodeOrder);
    const processed = new Set();
    for (let cursor = 0; cursor < queue.length; cursor += 1) {
      const node = queue[cursor];
      const nodeId = String(node.id);
      processed.add(nodeId);
      const targets = outgoing.get(nodeId).slice().sort((leftId, rightId) => stableNodeOrder(byId.get(leftId), byId.get(rightId)));
      for (const targetId of targets) {
        depths.set(targetId, Math.max(depths.get(targetId), depths.get(nodeId) + 1));
        incoming.set(targetId, incoming.get(targetId) - 1);
        if (incoming.get(targetId) === 0) queue.push(byId.get(targetId));
      }
    }

    if (processed.size !== nodes.length) {
      let fallbackDepth = 0;
      for (const nodeId of processed) fallbackDepth = Math.max(fallbackDepth, depths.get(nodeId) + 1);
      for (const node of nodes.slice().sort(stableNodeOrder)) {
        if (!processed.has(String(node.id))) depths.set(String(node.id), fallbackDepth);
      }
    }

    const columns = new Map();
    for (const node of nodes) {
      const depth = depths.get(String(node.id));
      if (!columns.has(depth)) columns.set(depth, []);
      columns.get(depth).push(node);
    }

    let maxRight = originX;
    let maxBottom = originY;
    let visualColumn = 0;
    for (const [_depth, column] of [...columns.entries()].sort((left, right) => left[0] - right[0])) {
      column.sort(stableNodeOrder);
      const lanes = [[]];
      let laneHeight = 0;
      for (const node of column) {
        node.width = NODE_WIDTH;
        node.height = compactNodeHeight(node);
        const projectedHeight = laneHeight + (lanes[lanes.length - 1].length ? ROW_GAP : 0) + node.height;
        if (lanes[lanes.length - 1].length && projectedHeight > MAX_COLUMN_HEIGHT) {
          lanes.push([]);
          laneHeight = 0;
        }
        lanes[lanes.length - 1].push(node);
        laneHeight += (lanes[lanes.length - 1].length > 1 ? ROW_GAP : 0) + node.height;
      }
      for (const lane of lanes) {
        let y = originY;
        for (const node of lane) {
          node.x = originX + visualColumn * (NODE_WIDTH + COLUMN_GAP);
          node.y = y;
          y += node.height + ROW_GAP;
          maxRight = Math.max(maxRight, node.x + node.width);
          maxBottom = Math.max(maxBottom, node.y + node.height);
        }
        visualColumn += 1;
      }
    }
    return { width: maxRight - originX, height: maxBottom - originY };
  }

  function compactWorkflowLayout(sourceNodes, sourceLinks = [], sourceGroups = []) {
    const nodes = (Array.isArray(sourceNodes) ? sourceNodes : []).map(node => ({ ...node }));
    const links = Array.isArray(sourceLinks) ? sourceLinks : [];
    const groups = (Array.isArray(sourceGroups) ? sourceGroups : []).map(group => ({ ...group }));
    const groupTitles = new Set(groups.map(group => String(group.title || "")));
    const topNodes = nodes.filter(node => !node.subgraph || !groupTitles.has(String(node.subgraph)));
    const topLayout = layoutScope(topNodes, links, SCENE_PADDING, SCENE_PADDING);

    let groupX = SCENE_PADDING + topLayout.width + (topNodes.length && groups.length ? GROUP_GAP : 0);
    let groupY = SCENE_PADDING;
    let maxRight = SCENE_PADDING + topLayout.width;
    let maxBottom = SCENE_PADDING + topLayout.height;

    for (const group of groups) {
      const members = nodes.filter(node => String(node.subgraph || "") === String(group.title || ""));
      const memberOriginX = groupX + GROUP_PADDING_X;
      const memberOriginY = groupY + GROUP_PADDING_TOP;
      const memberLayout = layoutScope(members, links, memberOriginX, memberOriginY);
      group.x = groupX;
      group.y = groupY;
      group.width = Math.max(220, memberLayout.width + GROUP_PADDING_X * 2);
      group.height = Math.max(180, memberLayout.height + GROUP_PADDING_TOP + GROUP_PADDING_BOTTOM);
      groupX = Math.max(groupX, group.x + group.width + GROUP_GAP);
      maxRight = Math.max(maxRight, group.x + group.width);
      maxBottom = Math.max(maxBottom, group.y + group.height);
    }

    return {
      nodes,
      groups,
      width: maxRight + SCENE_PADDING,
      height: maxBottom + SCENE_PADDING,
    };
  }

  return { compactNodeHeight, compactWorkflowLayout };
});

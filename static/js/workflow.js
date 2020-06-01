var g = new dagreD3.graphlib.Graph()
  .setGraph({})
  .setDefaultEdgeLabel(function() { return {}; });

// Here we"re setting nodeclass, which is used by our custom drawNodes function
// below.
g.setNode(0,  { label: "TOP",       class: "type-TOP" });
g.setNode(1,  { label: "S 1",         class: "type-S" });
g.setNode(2,  { label: "NP 2",        class: "type-NP" });
g.setNode(3,  { label: "DT 3",        class: "type-DT" });
g.setNode(4,  { label: "This 4",      class: "type-TK" });
g.setNode(5,  { label: "VP 5",        class: "type-VP" });
g.setNode(6,  { label: "VBZ 6",       class: "type-VBZ" });
g.setNode(7,  { label: "is 7",        class: "type-TK" });
g.setNode(8,  { label: "NP 8",        class: "type-NP" });
g.setNode(9,  { label: "DT 9",        class: "type-DT" });
g.setNode(10, { label: "an 10",        class: "type-TK" });
g.setNode(11, { label: "NN 11",        class: "type-NN" });
g.setNode(12, { label: "example 12",   class: "type-TK" });
g.setNode(13, { label: ". 13",         class: "type-." });
g.setNode(14, { label: "sentence 14",  class: "type-TK" });

g.nodes().forEach(function(v) {
  var node = g.node(v);
  // Round the corners of the nodes
  node.rx = node.ry = 5;
});

// Set up edges, no special attributes.
g.setEdge(2, 3);
g.setEdge(1, 2, {label: 'label text'});
g.setEdge(3, 4);
g.setEdge(6, 7);
g.setEdge(5, 6);
g.setEdge(9, 10);
g.setEdge(8, 9);
g.setEdge(11,12);
g.setEdge(8, 11);
g.setEdge(5, 8);
g.setEdge(1, 5);
g.setEdge(13,14);
g.setEdge(13,8, {label: "X"});
g.setEdge(1, 13);
g.setEdge(0, 1);

// Create the renderer
var render = new dagreD3.render();

// Set up an SVG group so that we can translate the final graph.
var svg = d3.select("svg"),
    svgGroup = svg.append("g");

// Run the renderer. This is what draws the final graph.
render(d3.select("svg g"), g);

// Center the graph
var xCenterOffset = (svg.attr("width") - g.graph().width) / 2;
svgGroup.attr("transform", "translate(" + xCenterOffset + ", 20)");
svg.attr("height", g.graph().height + 40);

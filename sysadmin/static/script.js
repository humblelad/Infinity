document.addEventListener('DOMContentLoaded', function() {
    const width = window.innerWidth;
    const height = window.innerHeight;
    let selectedNode = null;
    let root = null;


                fetch('/templates/colors.txt')
    .then(response => response.text())
    .then(data => {
        const colors = data.split('\n').reduce((acc, line) => {
            const [key, value] = line.split(':');
            acc[key.trim()] = value.trim();
            return acc;
        }, {});


        const tree = d3.tree().size([width, height - 160]);

        const svgContainer = d3.select(".svg-container");
        const svg = svgContainer.append("svg")
            .attr("width", width)
            .attr("height", height)
            .append("g")
            .attr("transform", "translate(0,100)");

        const tooltip = d3.select("body").append("div")
            .attr("class", "tooltip")
            .style("opacity", 0);

        document.getElementById('folderForm').addEventListener('submit', function (event) {
            event.preventDefault();
            const folderInput = document.getElementById('folderInput');
            const folderPath = folderInput.value.trim();
            const includeFiles = document.getElementById('includeFiles').checked;
            if (folderPath) {
                const folderName = folderPath.split('/').filter(Boolean).pop();
                d3.json(`/files?path=${encodeURIComponent(folderPath)}&include_files=${includeFiles}`).then(data => {
                    d3.select("svg").remove();

                    const svg = svgContainer.append("svg")
                        .attr("width", width)
                        .attr("height", height)
                        .append("g")
                        .attr("transform", "translate(0,100)");

                    root = d3.hierarchy({name: folderName, children: data}, d => d.children);
                    root.x0 = height / 2;
                    root.y0 = 0;

                    function collapse(d) {
                        if (d.children) {
                            d._children = d.children;
                            d._children.forEach(collapse);
                            d.children = null;
                        }
                    }

                    root.children.forEach(collapse);
                    update(root);

                    function update(source) {
                        const treeData = tree(root);
                        const nodes = treeData.descendants();
                        const links = treeData.descendants().slice(1);

                        nodes.forEach(d => d.y = d.depth * 150);

                        nodes.forEach(d => {
                            if (d.parent) {
                                const siblings = d.parent.children;
                                const siblingCount = siblings.length;
                                const siblingIndex = siblings.indexOf(d);
                                const totalWidth = (siblingCount - 1) * 100;
                                d.x = d.parent.x - totalWidth / 2 + siblingIndex * 100;
                            } else {
                                d.x = width / 2;
                            }
                        });

                        let i = 0;

                        const node = svg.selectAll('g.node')
                            .data(nodes, d => d.id || (d.id = ++i));

                        const nodeEnter = node.enter().append('g')
                            .attr('class', 'node')
                            .attr('transform', d => `translate(${source.x0},${source.y0})`)
                            .on('click', function (event, d) {
                                selectedNode = d;
                                collapseSiblings(d);
                                if (d.children) {
                                    d._children = d.children;
                                    d.children = null;
                                } else {
                                    d.children = d._children;
                                    d._children = null;
                                }
                                update(d);
                            })
                            .on('contextmenu', function (event, d) {
                                if (d !== root) {
                                    event.preventDefault();
                                    tooltip.transition()
                                        .duration(200)
                                        .style("opacity", .9);
                                    tooltip.html(`Permissions: ${d.data.permissions}<br>Owner: ${d.data.owner}<br>Group: ${d.data.group}`)
                                        .style("left", (event.pageX + 5) + "px")
                                        .style("top", (event.pageY - 28) + "px");
                                }
                            })
                            .on('mouseleave', function () {
                                tooltip.transition()
                                    .duration(200)
                                    .style("opacity", 0);
                            });

                        nodeEnter.append('circle')
                            .attr('class', 'node')
                            .attr('r', 1e-6)
                            .style('fill', d => d._children ? 'lightsteelblue' : '#fff');

                        nodeEnter.append('text')
                            .attr('dy', '.35em')
                            .attr('x', d => d.x < width / 2 ? -13 : 13)
                            .attr('text-anchor', d => d.x < width / 2 ? 'end' : 'start')
                            .text(d => d.data.name.length > 10 ? d.data.name.substring(0, 10) + '...' : d.data.name)
                            .append('title')
                            .text(d => d.data.name);

                        const nodeUpdate = nodeEnter.merge(node);

                        nodeUpdate.transition()
                            .duration(200)
                            .attr('transform', d => `translate(${d.x},${d.y})`);

                        nodeUpdate.select('circle.node')
                            .attr('r', 10)
                            .style('fill', d => d._children ? 'lightsteelblue' : '#fff')
                            .attr('cursor', 'pointer');

                        const nodeExit = node.exit().transition()
                            .duration(200)
                            .attr('transform', d => `translate(${source.x},${source.y})`)
                            .remove();

                        nodeExit.select('circle')
                            .attr('r', 1e-6);

                        nodeExit.select('text')
                            .style('fill-opacity', 1e-6);

                        const link = svg.selectAll('path.link')
                            .data(links, d => d.id);

                        const linkEnter = link.enter().insert('path', 'g')
                            .attr('class', 'link')
                            .attr('d', d => {
                                const o = {x: source.x0, y: source.y0};
                                return diagonal(o, o);
                            })
                            .style('stroke', d => colors[d.data.owner] || colors['others']);


                        const linkUpdate = linkEnter.merge(link);

                        linkUpdate.transition()
                            .duration(200)
                            .attr('d', d => diagonal(d, d.parent));

                        const linkExit = link.exit().transition()
                            .duration(200)
                            .attr('d', d => {
                                const o = {x: source.x, y: source.y};
                                return diagonal(o, o);
                            })
                            .remove();

                        nodes.forEach(d => {
                            d.x0 = d.x;
                            d.y0 = d.y;
                        });

                        const minX = d3.min(nodes, d => d.x);
                        const maxX = d3.max(nodes, d => d.x);
                        const svgWidth = Math.max(width, maxX - minX + 400);
                        const svgHeight = Math.max(height, d3.max(nodes, d => d.y) + 300);
                        svgContainer.select("svg")
                            .attr("width", svgWidth)
                            .attr("height", svgHeight)
                            .attr("viewBox", `${minX - 200} 0 ${svgWidth} ${svgHeight}`);

                        function diagonal(s, d) {
                            return `M${s.x},${s.y}
                                C${s.x},${(s.y + d.y) / 2}
                                 ${d.x},${(s.y + d.y) / 2}
                                 ${d.x},${d.y}`;
                        }
                    }

                    function collapseSiblings(node) {
                        if (node.parent) {
                            node.parent.children.forEach(sibling => {
                                if (sibling !== node && sibling.children) {
                                    sibling._children = sibling.children;
                                    sibling.children = null;
                                }
                            });
                        }
                    }

                    function collapseAllExcept(node) {
                        root.each(d => {
                            if (d !== node && d.children) {
                                d._children = d.children;
                                d.children = null;
                            }
                        });
                    }
                });
            }
        });

        function parsePermissions(permissions) {
            const meanings = {
                'r': 'Read',
                'w': 'Write',
                'x': 'Execute',
                '-': 'No'
            };

            const owner = `Owner: ${meanings[permissions[1]]}, ${meanings[permissions[2]]}, ${meanings[permissions[3]]} permissions`;
            const group = `Group: ${meanings[permissions[4]]}, ${meanings[permissions[5]]}, ${meanings[permissions[6]]} permissions`;
            const others = `Others: ${meanings[permissions[7]]}, ${meanings[permissions[8]]}, ${meanings[permissions[9]]} permissions`;

            return `${owner}<br>${group}<br>${others}`;
        }

        document.addEventListener('keydown', function (event) {
            if (event.code === 'Space' && selectedNode && selectedNode !== selectedNode.parent && selectedNode !== root) {
                document.getElementById('permissionForm').style.display = 'block';
                document.getElementById('permissionHeading').innerText = `You are changing file permission for "${selectedNode.data.name}"`;
                const permissionMeaning = parsePermissions(selectedNode.data.permissions);
                document.getElementById('permissionMeaning').innerHTML = permissionMeaning;
            }
        });

        document.getElementById('permissionForm').addEventListener('submit', function (event) {
            event.preventDefault();
            const newPermissions = document.getElementById('permissionInput').value;
            if (selectedNode) {
                fetch(`/update_permissions`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        path: selectedNode.data.path,
                        permissions: newPermissions
                    })
                }).then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            selectedNode.data.permissions = data.permissions;
                            alert('Permissions updated successfully');
                        } else {
                            alert('Failed to update permissions');
                        }
                        document.getElementById('permissionInput').value = '';
                    });
            }
        });
    });
    });

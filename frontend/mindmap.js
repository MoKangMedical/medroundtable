// mindmap.js - 讨论思维导图生成器

class DiscussionMindMap {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.width = this.container.clientWidth;
        this.height = 600;
        this.svg = null;
        this.g = null;
        this.zoom = null;
        this.nodes = [];
        this.links = [];
    }

    // 解析讨论内容生成思维导图数据
    parseDiscussion(messages, clinicalQuestion) {
        const root = {
            id: 'root',
            label: clinicalQuestion || '研究讨论',
            type: 'root',
            children: []
        };

        // 分析消息提取关键信息
        const sections = {
            '研究背景': [],
            '研究设计': [],
            '研究对象': [],
            '干预措施': [],
            '终点指标': [],
            '统计方法': [],
            '执行方案': [],
            '关键建议': []
        };

        messages.forEach(msg => {
            const content = msg.content || '';
            const role = msg.from_role;

            // 根据角色和内容分类
            if (role === 'phd_student') {
                this.extractKeyPoints(content, sections['研究背景'], ['背景', '现状', '文献']);
            } else if (role === 'epidemiologist') {
                this.extractKeyPoints(content, sections['研究设计'], ['设计', '类型', '方法']);
                this.extractKeyPoints(content, sections['研究对象'], ['纳入', '排除', '样本']);
            } else if (role === 'clinical_director') {
                this.extractKeyPoints(content, sections['干预措施'], ['干预', '治疗', '对照']);
                this.extractKeyPoints(content, sections['终点指标'], ['终点', '指标', '疗效']);
            } else if (role === 'statistician') {
                this.extractKeyPoints(content, sections['统计方法'], ['统计', '分析', '检验']);
            } else if (role === 'research_nurse') {
                this.extractKeyPoints(content, sections['执行方案'], ['流程', '访视', '采集']);
            }

            // 提取关键建议
            this.extractKeyPoints(content, sections['关键建议'], ['建议', '注意', '重要']);
        });

        // 构建树形结构
        Object.entries(sections).forEach(([category, points]) => {
            if (points.length > 0) {
                root.children.push({
                    id: category,
                    label: category,
                    type: 'category',
                    children: points.map((p, i) => ({
                        id: `${category}_${i}`,
                        label: p,
                        type: 'detail'
                    }))
                });
            }
        });

        return this.flattenTree(root);
    }

    extractKeyPoints(content, targetArray, keywords) {
        const sentences = content.split(/[。！？\n]/);
        sentences.forEach(sentence => {
            const trimmed = sentence.trim();
            if (trimmed.length > 10 && trimmed.length < 100) {
                // 检查是否包含关键词
                const hasKeyword = keywords.some(kw => trimmed.includes(kw));
                // 或者是重要结论（包含数字）
                const hasNumber = /\d+/.test(trimmed);
                
                if ((hasKeyword || hasNumber) && !targetArray.includes(trimmed)) {
                    targetArray.push(trimmed);
                }
            }
        });
    }

    flattenTree(root) {
        const nodes = [];
        const links = [];
        let id = 0;

        function traverse(node, parentId, level) {
            const nodeId = id++;
            nodes.push({
                id: nodeId,
                label: node.label,
                type: node.type,
                level: level
            });

            if (parentId !== null) {
                links.push({
                    source: parentId,
                    target: nodeId
                });
            }

            if (node.children) {
                node.children.forEach(child => traverse(child, nodeId, level + 1));
            }

            return nodeId;
        }

        traverse(root, null, 0);
        return { nodes, links };
    }

    // 渲染思维导图
    render(data) {
        this.nodes = data.nodes;
        this.links = data.links;

        // 清空容器
        this.container.innerHTML = '';

        // 创建SVG
        this.svg = d3.select(this.container)
            .append('svg')
            .attr('width', this.width)
            .attr('height', this.height)
            .attr('viewBox', [0, 0, this.width, this.height]);

        // 添加缩放功能
        this.zoom = d3.zoom()
            .scaleExtent([0.5, 2])
            .on('zoom', (event) => {
                this.g.attr('transform', event.transform);
            });

        this.svg.call(this.zoom);

        // 创建主组
        this.g = this.svg.append('g')
            .attr('transform', `translate(${this.width / 2}, ${this.height / 2})`);

        // 使用力导向布局
        const simulation = d3.forceSimulation(this.nodes)
            .force('link', d3.forceLink(this.links).id(d => d.id).distance(100))
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(0, 0))
            .force('collision', d3.forceCollide().radius(60));

        // 绘制连线
        const link = this.g.append('g')
            .selectAll('line')
            .data(this.links)
            .join('line')
            .attr('stroke', '#94a3b8')
            .attr('stroke-width', 2)
            .attr('stroke-opacity', 0.6);

        // 绘制节点组
        const node = this.g.append('g')
            .selectAll('g')
            .data(this.nodes)
            .join('g')
            .attr('class', 'mindmap-node')
            .call(d3.drag()
                .on('start', (event, d) => {
                    if (!event.active) simulation.alphaTarget(0.3).restart();
                    d.fx = d.x;
                    d.fy = d.y;
                })
                .on('drag', (event, d) => {
                    d.fx = event.x;
                    d.fy = event.y;
                })
                .on('end', (event, d) => {
                    if (!event.active) simulation.alphaTarget(0);
                    d.fx = null;
                    d.fy = null;
                }));

        // 绘制节点圆形
        node.append('circle')
            .attr('r', d => {
                if (d.type === 'root') return 50;
                if (d.type === 'category') return 35;
                return 25;
            })
            .attr('fill', d => {
                if (d.type === 'root') return '#3b82f6';
                if (d.type === 'category') return '#10b981';
                return '#f59e0b';
            })
            .attr('stroke', '#fff')
            .attr('stroke-width', 3)
            .style('cursor', 'pointer')
            .on('mouseover', function() {
                d3.select(this).attr('stroke', '#fbbf24').attr('stroke-width', 4);
            })
            .on('mouseout', function() {
                d3.select(this).attr('stroke', '#fff').attr('stroke-width', 3);
            })
            .on('click', function(event, d) {
                event.stopPropagation();
                showNodeDetail(d);
            });

        // 添加节点文字
        node.append('text')
            .text(d => {
                const maxLen = d.type === 'root' ? 12 : (d.type === 'category' ? 10 : 8);
                return d.label.length > maxLen ? d.label.substring(0, maxLen) + '...' : d.label;
            })
            .attr('text-anchor', 'middle')
            .attr('dy', '.35em')
            .attr('fill', '#fff')
            .attr('font-size', d => {
                if (d.type === 'root') return '14px';
                if (d.type === 'category') return '12px';
                return '10px';
            })
            .attr('font-weight', d => d.type === 'root' ? 'bold' : 'normal')
            .style('pointer-events', 'none');

        // 添加完整标签提示
        node.append('title')
            .text(d => d.label);

        // 更新位置
        simulation.on('tick', () => {
            link
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);

            node
                .attr('transform', d => `translate(${d.x},${d.y})`);
        });

        // 初始缩放以适应
        setTimeout(() => {
            this.svg.transition().duration(750).call(
                this.zoom.transform,
                d3.zoomIdentity.translate(this.width / 2, this.height / 2).scale(0.8)
            );
        }, 100);
    }

    // 重置视图
    resetView() {
        if (this.svg && this.zoom) {
            this.svg.transition().duration(750).call(
                this.zoom.transform,
                d3.zoomIdentity.translate(this.width / 2, this.height / 2).scale(0.8)
            );
        }
    }

    // 导出为图片
    exportImage() {
        if (!this.svg) return;
        
        const svgData = new XMLSerializer().serializeToString(this.svg.node());
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const img = new Image();
        
        canvas.width = this.width;
        canvas.height = this.height;
        
        img.onload = () => {
            ctx.fillStyle = '#fff';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.drawImage(img, 0, 0);
            
            const link = document.createElement('a');
            link.download = `讨论思维导图_${new Date().toISOString().split('T')[0]}.png`;
            link.href = canvas.toDataURL('image/png');
            link.click();
        };
        
        img.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgData)));
    }
}

// 全局实例
let mindMap = null;

// 初始化思维导图
function initMindMap() {
    mindMap = new DiscussionMindMap('mindmapContainer');
}

// 更新思维导图
function updateMindMap(messages, clinicalQuestion) {
    if (!mindMap) {
        initMindMap();
    }
    const data = mindMap.parseDiscussion(messages, clinicalQuestion);
    mindMap.render(data);
}

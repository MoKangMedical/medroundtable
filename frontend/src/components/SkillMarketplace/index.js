import React, { useState, useEffect } from 'react';
import { Search, Database, FlaskConical, FileText, Pill, Activity, BookOpen, Zap } from 'lucide-react';
import './SkillMarketplace.css';

// 技能分类图标映射
const categoryIcons = {
  '临床': Activity,
  '研究': BookOpen,
  '生物信息学': FlaskConical,
  '法规合规': FileText,
  'AI_ML': Zap,
  '数据库': Database,
  '文献': BookOpen,
  '临床试验': Activity,
  '药物研发': Pill,
  '通用': Zap
};

// 技能分类颜色
const categoryColors = {
  '临床': '#10b981',
  '研究': '#3b82f6',
  '生物信息学': '#8b5cf6',
  '法规合规': '#f59e0b',
  'AI_ML': '#ec4899',
  '数据库': '#06b6d4',
  '文献': '#6366f1',
  '临床试验': '#14b8a6',
  '药物研发': '#f97316',
  '通用': '#6b7280'
};

const SkillMarketplace = () => {
  const [skills, setSkills] = useState([]);
  const [categories, setCategories] = useState([]);
  const [stats, setStats] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
    fetchCategories();
    fetchSkills();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await fetch('/api/v2/stats');
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('获取统计失败:', error);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await fetch('/api/v2/skills/categories');
      const data = await response.json();
      setCategories(data);
    } catch (error) {
      console.error('获取分类失败:', error);
    }
  };

  const fetchSkills = async (category = null, search = '') => {
    setLoading(true);
    try {
      let url = '/api/v2/skills/';
      const params = new URLSearchParams();
      if (category) params.append('category', category);
      if (search) {
        url = '/api/v2/skills/search?q=' + encodeURIComponent(search);
      }
      if (params.toString()) url += '?' + params.toString();

      const response = await fetch(url);
      const data = await response.json();
      setSkills(data);
    } catch (error) {
      console.error('获取技能失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    const query = e.target.value;
    setSearchQuery(query);
    fetchSkills(selectedCategory, query);
  };

  const handleCategoryClick = (category) => {
    const newCategory = selectedCategory === category ? null : category;
    setSelectedCategory(newCategory);
    fetchSkills(newCategory, searchQuery);
  };

  const invokeSkill = async (skillId) => {
    try {
      const response = await fetch(`/api/v2/skills/${skillId}/invoke`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          skill_id: skillId,
          parameters: {}
        })
      });
      const data = await response.json();
      alert(`技能调用结果: ${data.message}`);
    } catch (error) {
      console.error('调用技能失败:', error);
    }
  };

  return (
    <div className="skill-marketplace">
      {/* 头部区域 */}
      <div className="marketplace-header">
        <h1>🎯 技能市场</h1>
        <p className="subtitle">探索 997 项专业科研技能，赋能您的医学研究</p>
        
        {/* 搜索框 */}
        <div className="search-box">
          <Search className="search-icon" size={20} />
          <input
            type="text"
            placeholder="搜索技能 (例如: PubMed, 临床试验, 单细胞分析...)"
            value={searchQuery}
            onChange={handleSearch}
          />
        </div>
      </div>

      {/* 统计卡片 */}
      {stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-number">{stats.skills?.total_skills || 0}</div>
            <div className="stat-label">总技能数</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">{stats.databases?.total || 0}</div>
            <div className="stat-label">数据库</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">{stats.agents?.total || 0}</div>
            <div className="stat-label">专业Agent</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">{categories?.length || 0}</div>
            <div className="stat-label">技能分类</div>
          </div>
        </div>
      )}

      {/* 分类筛选 */}
      <div className="category-filter">
        <h3>📂 按分类浏览</h3>
        <div className="category-tags">
          {categories.map((cat) => {
            const Icon = categoryIcons[cat.name] || Zap;
            const isSelected = selectedCategory === cat.name;
            return (
              <button
                key={cat.name}
                className={`category-tag ${isSelected ? 'selected' : ''}`}
                onClick={() => handleCategoryClick(cat.name)}
                style={{
                  backgroundColor: isSelected ? categoryColors[cat.name] : 'transparent',
                  borderColor: categoryColors[cat.name]
                }}
              >
                <Icon size={16} />
                <span>{cat.name}</span>
                <span className="count">({cat.count})</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* 技能列表 */}
      <div className="skills-section">
        <h3>🔧 {selectedCategory ? `${selectedCategory}技能` : '全部技能'}</h3>
        
        {loading ? (
          <div className="loading">加载中...</div>
        ) : (
          <div className="skills-grid">
            {skills.map((skill) => {
              const Icon = categoryIcons[skill.category] || Zap;
              return (
                <div key={skill.id} className="skill-card">
                  <div 
                    className="skill-category-badge"
                    style={{ backgroundColor: categoryColors[skill.category] || '#6b7280' }}
                  >
                    <Icon size={14} />
                    <span>{skill.category}</span>
                  </div>
                  <h4 className="skill-name">{skill.name}</h4>
                  <p className="skill-description">{skill.description}</p>
                  <div className="skill-meta">
                    <span className="skill-source">{skill.source}</span>
                    <span className="skill-version">v{skill.version}</span>
                  </div>
                  <button 
                    className="invoke-btn"
                    onClick={() => invokeSkill(skill.id)}
                    disabled={!skill.enabled}
                  >
                    {skill.enabled ? '▶ 使用技能' : '⏸ 未启用'}
                  </button>
                </div>
              );
            })}
          </div>
        )}
        
        {!loading && skills.length === 0 && (
          <div className="no-results">
            <p>未找到匹配的技能</p>
            <button onClick={() => {setSearchQuery(''); setSelectedCategory(null); fetchSkills();}}>
              清除筛选
            </button>
          </div>
        )}
      </div>

      {/* 特色功能 */}
      <div className="featured-section">
        <h3>⭐ 特色功能</h3>
        <div className="featured-grid">
          <div className="featured-card">
            <Database size={32} color="#06b6d4" />
            <h4>数据库浏览器</h4>
            <p>统一访问40+生物医学数据库</p>
          </div>
          <div className="featured-card">
            <Activity size={32} color="#14b8a6" />
            <h4>临床试验设计</h4>
            <p>智能生成试验方案、入排标准</p>
          </div>
          <div className="featured-card">
            <FlaskConical size={32} color="#8b5cf6" />
            <h4>生物信息学</h4>
            <p>单细胞分析、变异注释、通路分析</p>
          </div>
          <div className="featured-card">
            <BookOpen size={32} color="#6366f1" />
            <h4>文献挖掘</h4>
            <p>AI驱动的文献检索和综述生成</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SkillMarketplace;

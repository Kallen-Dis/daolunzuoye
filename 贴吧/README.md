# 百度贴吧游戏数据可视化分析项目

## 项目简介

本项目通过Python爬虫技术采集百度贴吧的游戏相关数据，进行数据清洗、统计分析和可视化展示，深入挖掘游戏社区的热点趋势、用户行为模式和情感倾向。项目成果可为游戏运营、内容创作和市场分析提供数据支持。

## 技术栈

- **爬虫技术**：Python、Requests、BeautifulSoup4
- **数据分析**：Pandas、NumPy
- **数据可视化**：Matplotlib、Seaborn
- **文本处理**：Jieba分词

## 目录结构

`
游戏数据可视化分析项目/
 data/                    # 数据文件目录
    raw_data.csv         # 原始爬虫数据
    cleaned_data.csv     # 清洗后数据
    processed_data.csv   # 处理后数据
 visualizations/          # 可视化图表目录（15张图表）
    hot_games.png        # 热门游戏热度图
    hot_host_games.png   # 主机游戏热门度图
    hot_mobile_games.png # 手游热门度图
    cross_platform_games.png # 跨平台游戏对比图
    post_trend.png       # 游戏热度时间趋势图
    game_type_distribution.png # 游戏类型分布饼图
    game_type_trend.png  # 游戏类型时间趋势图
    comments_posts_scatter.png # 评论与帖子关系散点图
    sentiment_pie.png    # 游戏评价情感分析饼图
    length_reply_scatter.png # 帖子长度与回复数散点图
    avg_replies_by_length.png # 不同长度区间平均回复数图
    top_game_keywords.png # 热门游戏讨论关键词TOP20
    avg_replies_by_hour.png # 发布时间（小时）与回复数关系图
    avg_replies_by_day.png # 发布时间（星期）与回复数关系图
    game_type_replies.png # 游戏类型与回复数关系图
 scripts/                 # 脚本文件目录
    crawler.py           # 贴吧爬虫主程序
    data_cleaner.py      # 数据清洗脚本
    analyzer.py          # 数据分析脚本
    visualizer.py        # 可视化生成脚本
 游戏数据可视化分析汇报.md   # 完整项目报告
 游戏数据可视化分析演讲文稿.md # 项目演讲文稿
 README.md                # 项目说明文档
`

## 安装与依赖

1. 克隆或下载项目到本地
2. 安装所需依赖：

`ash
pip install requests beautifulsoup4 pandas numpy matplotlib seaborn jieba
`

## 使用方法

### 1. 数据采集

运行爬虫脚本采集百度贴吧数据：

`ash
python scripts/crawler.py
`

爬虫会自动访问百度贴吧，采集游戏相关帖子和评论数据，保存至 data/raw_data.csv

### 2. 数据清洗

执行数据清洗脚本处理原始数据：

`ash
python scripts/data_cleaner.py
`

清洗过程包括：
- 内容筛选（基于35个游戏关键词和40个游戏论坛白名单）
- 异常值处理（IQR方法）
- 数据去重
清洗后的数据保存至 data/cleaned_data.csv

### 3. 数据分析

运行数据分析脚本：

`ash
python scripts/analyzer.py
`

分析内容包括：
- 游戏热度统计
- 用户行为分析
- 情感倾向分析
- 关键词提取
分析结果保存至 data/processed_data.csv

### 4. 可视化生成

执行可视化脚本生成图表：

`ash
python scripts/visualizer.py
`

生成的15张可视化图表将保存至 isualizations/ 目录

## 项目成果

### 数据规模
- 原始数据：1397个帖子，5319条评论
- 筛选后：1346个帖子，3252条评论
- 去重后：626个帖子，562条评论

### 核心发现

1. **游戏热度排行**
   - 主机游戏：原神（10次提及）、最终幻想（8次）、战神（7次）
   - 手游：原神（9次）、和平精英（7次）、王者荣耀（6次）
   - 原神作为跨平台游戏成为讨论焦点

2. **用户行为模式**
   - 发布时间：周日和12点是获取最高回复的黄金时段
   - 帖子长度：101-200字的内容平均回复数最高

3. **情感分析**
   - 中性：53.83%
   - 正面：34.35%
   - 非常正面：4.47%
   - 负面：7.35%

## 项目报告

完整项目报告请查看 游戏数据可视化分析汇报.md
项目演讲文稿请查看 游戏数据可视化分析演讲文稿.md

## 运行环境

- Python 3.7+
- Windows/Linux/macOS

## 注意事项

1. 爬虫运行时请遵守网站robots协议，合理设置爬取间隔
2. 数据使用请尊重用户隐私和平台规定
3. 如需扩展数据来源，请修改 scripts/crawler.py 中的配置参数

## 未来改进方向

1. 扩展数据来源至社交媒体、游戏平台等多渠道
2. 引入机器学习算法进行更深入的情感分析
3. 开发交互式可视化界面
4. 实现实时数据监控功能

## 贡献者

- 项目负责人：[你的名字]
- 技术支持：[如果有合作者可添加]

## 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件

---

**项目日期**：2025年12月26日

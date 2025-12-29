import os
import json
import pandas as pd
import re
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 1. 读取所有数据文件
def load_all_data():
    data_dir = 'c:\\Users\\23120\\Desktop\\贴吧'
    all_contents = []
    all_comments = []
    
    # 遍历所有子目录
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if 'content' in file or 'contents' in file:
                            all_contents.extend(data)
                        elif 'comment' in file or 'comments' in file:
                            all_comments.extend(data)
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    
    return all_contents, all_comments

# 2. 筛选与游戏相关的内容
def filter_game_related(data):
    # 游戏相关关键词（更广泛的游戏术语）
    game_keywords = ['游戏', '网游', '手游', '端游', '电竞', 'steam', 'ps5', 'xbox', 'switch',
                    '主机', '掌机', 'pc', '单机', '在线', '多人', '竞技', '副本', '剧情',
                    '装备', '角色', '升级', '任务', '成就', '皮肤', '道具', '攻略', '测评',
                    'mod', '补丁', 'DLC', '画质', '帧率', '卡顿', '流畅', '操作', '手感',
                    '存档', '加载', '闪退', 'bug', '更新', '版本', '发售', '预售', '折扣',
                    '推荐', '对比', '选择', '配置', '需求', '安装', '下载', '账号', '登录']
    
    # 明确的游戏相关贴吧名称
    gaming_tiebas = ['游戏', '主机游戏', 'steam', 'ps5', 'xbox', 'switch', '手游', '电竞',
                     '网络游戏', '单机游戏', '图拉丁', '电脑吧', '显卡', '游戏推荐', '英雄联盟',
                     '游戏王', '原神', '塞尔达', '战神', '地平线', '宝可梦', '马里奥', '最终幻想',
                     '王者荣耀', '和平精英', 'pubg', 'csgo', 'dota', 'lol', '守望先锋', 'apex',
                     'valorant', 'gta', '赛博朋克', '巫师', '刺客信条', '荒野大镖客']
    
    filtered_data = []
    for item in data:
        # 检查内容是否包含游戏相关关键词
        text = ''
        
        # 处理帖子数据
        if 'title' in item:
            text += item['title'] + ' '
        if 'desc' in item and item['desc']:
            text += item['desc'] + ' '
        if 'tieba_name' in item:
            text += item['tieba_name'] + ' '
        
        # 处理评论数据
        if 'content' in item:
            text += item['content'] + ' '
        
        # 1. 优先检查是否来自游戏相关贴吧
        if 'tieba_name' in item:
            tieba_name = item['tieba_name']
            if any(gaming_tieba in tieba_name for gaming_tieba in gaming_tiebas):
                filtered_data.append(item)
                continue
        
        # 2. 检查是否包含广泛的游戏相关术语
        if any(keyword in text for keyword in game_keywords):
            filtered_data.append(item)
            continue
    
    return filtered_data

# 3. 去重
def remove_duplicates(data):
    # 根据note_id或唯一标识符去重
    seen = set()
    unique_data = []
    for item in data:
        if 'note_id' in item:
            key = item['note_id']
        elif 'comment_id' in item:
            key = item['comment_id']
        else:
            # 对于没有明确ID的，使用标题+描述+发布时间作为唯一标识
            key = f"{item.get('title', '')}-{item.get('desc', '')}-{item.get('publish_time', '')}"
        
        if key not in seen:
            seen.add(key)
            unique_data.append(item)
    
    return unique_data

# 4. 分析数据
def analyze_data(contents, comments):
    analysis_results = {}
    
    # 转换为DataFrame便于分析
    df_contents = pd.DataFrame(contents)
    df_comments = pd.DataFrame(comments)
    
    print("=== 数据基本信息 ===")
    print(f"总帖子数: {len(df_contents)}")
    print(f"总评论数: {len(df_comments)}")
    
    # 4.1 游戏热度分析（按贴吧）
    print("\n=== 游戏热度分析（按贴吧） ===")
    tieba_counts = df_contents['tieba_name'].value_counts().head(10)
    analysis_results['tieba_counts'] = tieba_counts
    print(tieba_counts)
    
    # 4.2 热门游戏分析（从标题和描述中提取游戏名称）
    print("\n=== 热门游戏分析 ===")
    
    # 平台相关关键词（用于分类）
    platform_keywords = {
        '主机': ['ps5', 'xbox', 'switch', '主机', 'playstation', 'ps4', 'ps3', 'xbox series', 'xbox one'],
        '手游': ['手机', '手游', '移动端', '安卓', 'ios', 'app', '手游推荐', '手机游戏']
    }
    
    # 创建游戏分类列表（去重）
    game_categories = {
        '主机游戏': list(set(['塞尔达', '赛博朋克2077', '巫师3', '刺客信条', '荒野大镖客2',
                   'gta5', '原神', '最终幻想', '战神', '地平线', '漫威蜘蛛侠',
                   '塞尔达传说', '马里奥', '宝可梦', '暗黑破坏神', '星际争霸', '红警'])),
        '手游': list(set(['王者荣耀', '和平精英', 'lol', 'csgo', 'pubg', '原神', '三国杀',
               '饥荒', '我的世界', '泰拉瑞亚', 'among us', '糖豆人', 'apex', 'valorant',
               '吃鸡']))
    }
    
    # 合并所有游戏
    common_games = list(set(game_categories['主机游戏'] + game_categories['手游']))
    
    # 统计各游戏出现次数
    game_counts = Counter()
    host_game_counts = Counter()
    mobile_game_counts = Counter()
    platform_only_host = 0  # 仅通过平台关键词判断为主机的内容数
    platform_only_mobile = 0  # 仅通过平台关键词判断为手游的内容数
    
    for index, row in df_contents.iterrows():
        text = f"{row.get('title', '')} {row.get('desc', '')} {row.get('tieba_name', '')}"
        game_detected = False
        platform_detected = False
        
        # 1. 检测明确的游戏名称
        for game in common_games:
            if game in text:
                game_counts[game] += 1
                game_detected = True
                # 根据分类更新对应计数器
                if game in game_categories['主机游戏']:
                    host_game_counts[game] += 1
                if game in game_categories['手游']:
                    mobile_game_counts[game] += 1
        
        # 2. 如果没有检测到明确的游戏名称，基于平台关键词分类
        if not game_detected:
            # 检测主机平台关键词
            if any(platform in text.lower() for platform in platform_keywords['主机']):
                platform_only_host += 1
                # 可以增加一个通用的主机游戏计数器
                host_game_counts['[主机平台内容]'] += 1
                platform_detected = True
            
            # 检测手游平台关键词
            if any(platform in text.lower() for platform in platform_keywords['手游']):
                platform_only_mobile += 1
                # 可以增加一个通用的手游计数器
                mobile_game_counts['[手游平台内容]'] += 1
                platform_detected = True
    
    print(f"\n平台分类补充信息:")
    print(f"仅通过主机平台关键词判断的内容数: {platform_only_host}")
    print(f"仅通过手游平台关键词判断的内容数: {platform_only_mobile}")
    
    # 输出整体热门游戏
    top_games = game_counts.most_common(10)
    analysis_results['game_counts'] = top_games
    print("\n整体热门游戏TOP10：")
    print(top_games)
    
    # 输出主机游戏热度排名
    top_host_games = host_game_counts.most_common(10)
    analysis_results['host_game_counts'] = top_host_games
    print("\n主机游戏热度TOP10：")
    print(top_host_games)
    
    # 输出手游热度排名
    top_mobile_games = mobile_game_counts.most_common(10)
    analysis_results['mobile_game_counts'] = top_mobile_games
    print("\n手游热度TOP10：")
    print(top_mobile_games)
    
    # 4.2.3 双平台游戏分析（同时出现在主机和手游）
    print("\n=== 双平台游戏分析 ===")
    host_game_names = set([game for game, count in host_game_counts.most_common() if game != '[主机平台内容]'])
    mobile_game_names = set([game for game, count in mobile_game_counts.most_common() if game != '[手游平台内容]'])
    
    # 找出同时出现在主机和手游的游戏
    cross_platform_games = host_game_names.intersection(mobile_game_names)
    
    if cross_platform_games:
        print(f"双平台游戏数量：{len(cross_platform_games)}")
        print("双平台游戏列表：")
        for game in cross_platform_games:
            host_count = host_game_counts[game]
            mobile_count = mobile_game_counts[game]
            total_count = host_count + mobile_count
            print(f"{game}: 主机提及{host_count}次，手游提及{mobile_count}次，总提及{total_count}次")
        analysis_results['cross_platform_games'] = list(cross_platform_games)
    else:
        print("未发现双平台游戏")
        analysis_results['cross_platform_games'] = []
    
    # 4.3 帖子回复数分析
    print("\n=== 帖子回复数分析 ===")
    if 'total_replay_num' in df_contents.columns:
        # 检测并处理回复数异常值
        replies = df_contents['total_replay_num']
        
        # 使用四分位距法检测异常值
        Q1 = replies.quantile(0.25)
        Q3 = replies.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        # 过滤异常值
        filtered_replies = replies[(replies >= lower_bound) & (replies <= upper_bound)]
        
        # 计算统计信息
        avg_replies = filtered_replies.mean()
        max_replies = filtered_replies.max()
        min_replies = filtered_replies.min()
        
        # 统计异常值数量
        outlier_count = len(replies) - len(filtered_replies)
        
        analysis_results['replies_stats'] = {
            'avg': avg_replies,
            'max': max_replies,
            'min': min_replies,
            'outlier_count': outlier_count
        }
        
        print(f"平均回复数: {avg_replies:.2f}")
        print(f"最大回复数: {max_replies}")
        print(f"最小回复数: {min_replies}")
        print(f"异常值数量: {outlier_count}")
        print(f"有效数据占比: {len(filtered_replies)/len(replies)*100:.2f}%")
    
    # 4.4 发布时间分析与游戏类型关系
    print("\n=== 发布时间分析 ===")
    if 'publish_time' in df_contents.columns:
        # 转换发布时间为datetime
        df_contents['publish_time'] = pd.to_datetime(df_contents['publish_time'], errors='coerce')
        # 按日期统计帖子数量
        daily_posts = df_contents['publish_time'].dt.date.value_counts().sort_index()
        analysis_results['daily_posts'] = daily_posts
        print(daily_posts)
        
        # 4.4.1 按游戏类型分析时间趋势
        print("\n=== 游戏类型时间趋势分析 ===")
        
        # 为每个帖子分类游戏类型
        def classify_game_type(text):
            text_lower = text.lower()
            is_host = any(platform in text_lower for platform in platform_keywords['主机'])
            is_mobile = any(platform in text_lower for platform in platform_keywords['手游'])
            
            if is_host and is_mobile:
                return '双平台'
            elif is_host:
                return '主机'
            elif is_mobile:
                return '手游'
            else:
                return '其他'
        
        # 添加游戏类型列
        df_contents['game_type'] = df_contents.apply(lambda row: classify_game_type(f"{row.get('title', '')} {row.get('desc', '')} {row.get('tieba_name', '')}"), axis=1)
        analysis_results['game_type_distribution'] = df_contents['game_type'].value_counts().to_dict()
        
        print("游戏类型分布:")
        print(df_contents['game_type'].value_counts())
        
        # 分析不同游戏类型的时间趋势
        df_time_type = df_contents[['publish_time', 'game_type']].copy()
        df_time_type = df_time_type.dropna()
        
        if not df_time_type.empty:
            # 按月统计不同游戏类型的帖子数量
            df_time_type['month'] = df_time_type['publish_time'].dt.to_period('M')
            monthly_type_counts = df_time_type.groupby(['month', 'game_type']).size().unstack(fill_value=0)
            analysis_results['monthly_type_counts'] = monthly_type_counts
            print("\n不同游戏类型的月度分布:")
            print(monthly_type_counts)
    
    # 4.5 评论与帖子关系分析
    print("\n=== 评论与帖子关系分析 ===")
    if not df_comments.empty:
        # 计算每个帖子的评论数
        comments_per_post = df_comments['note_id'].value_counts()
        analysis_results['comments_per_post'] = comments_per_post.to_dict()
        
        print(f"评论覆盖的帖子数: {len(comments_per_post)}")
        print(f"平均每个帖子的评论数: {df_comments.shape[0]/df_contents.shape[0]:.2f}")
        print(f"评论最多的帖子TOP5:")
        top_commented_posts = comments_per_post.head(5)
        for note_id, count in top_commented_posts.items():
            # 查找对应的帖子标题
            post_title = df_contents[df_contents['note_id'] == note_id]['title'].values[0] if len(df_contents[df_contents['note_id'] == note_id]) > 0 else '未知标题'
            print(f"{post_title[:20]}...: {count}条评论")
        
        # 4.5.1 分析评论数与回复数的关系
        if 'total_replay_num' in df_contents.columns:
            # 合并评论数和回复数
            df_comments_merge = pd.DataFrame({'note_id': comments_per_post.index, 'comment_count': comments_per_post.values})
            df_combined = pd.merge(df_contents, df_comments_merge, on='note_id', how='left')
            df_combined['comment_count'] = df_combined['comment_count'].fillna(0)
            
            # 计算相关性
            if len(df_combined) > 1:
                correlation = df_combined['total_replay_num'].corr(df_combined['comment_count'])
                print(f"\n帖子回复数与评论数的相关性: {correlation:.2f}")
                analysis_results['reply_comment_correlation'] = correlation
    
    # 4.6 好评率分析（简单版：根据关键词判断正面评价）
    print("\n=== 好评率分析 ===")
    positive_keywords = ['好玩', '不错', '喜欢', '推荐', '好评', '优秀', '神作', '给力', '良心', '精彩']
    negative_keywords = ['垃圾', '不好玩', '失望', '差评', '坑', '骗钱', '垃圾', '卸载', '后悔', '无聊']
    
    positive_count = 0
    negative_count = 0
    neutral_count = 0
    total_count = 0
    
    for index, row in df_contents.iterrows():
        text = f"{row.get('title', '')} {row.get('desc', '')}"
        has_positive = any(keyword in text for keyword in positive_keywords)
        has_negative = any(keyword in text for keyword in negative_keywords)
        
        total_count += 1
        if has_positive and not has_negative:
            positive_count += 1
        elif has_negative and not has_positive:
            negative_count += 1
        elif has_positive and has_negative:
            # 同时包含正面和负面关键词，计入中性
            neutral_count += 1
        else:
            neutral_count += 1
    
    if total_count > 0:
        positive_rate = (positive_count / total_count) * 100
        negative_rate = (negative_count / total_count) * 100
        neutral_rate = (neutral_count / total_count) * 100
        analysis_results['sentiment_stats'] = {
            'positive_rate': positive_rate,
            'negative_rate': negative_rate,
            'neutral_rate': neutral_rate,
            'total_count': total_count
        }
        print(f"总帖子数: {total_count}")
        print(f"好评数: {positive_count}, 好评率: {positive_rate:.2f}%")
        print(f"差评数: {negative_count}, 差评率: {negative_rate:.2f}%")
        print(f"中性数: {neutral_count}, 中性率: {neutral_rate:.2f}%")
    
    # 4.7 帖子长度与回复数相关性分析
    print("\n=== 帖子长度与回复数相关性分析 ===")
    if 'total_replay_num' in df_contents.columns:
        # 计算帖子总长度（标题+描述字符数）
        df_contents['post_length'] = df_contents.apply(lambda row: len(str(row.get('title', ''))) + len(str(row.get('desc', ''))), axis=1)
        
        # 只分析有回复的帖子
        df_with_replies = df_contents[df_contents['total_replay_num'] > 0]
        
        if len(df_with_replies) > 1:
            # 计算相关性
            correlation = df_with_replies['post_length'].corr(df_with_replies['total_replay_num'])
            print(f"帖子长度与回复数的相关性: {correlation:.2f}")
            analysis_results['length_reply_correlation'] = correlation
            
            # 分析不同长度区间的平均回复数
            bins = [0, 50, 100, 200, 300, 500, float('inf')]
            labels = ['0-50字', '51-100字', '101-200字', '201-300字', '301-500字', '500字以上']
            df_with_replies['length_range'] = pd.cut(df_with_replies['post_length'], bins=bins, labels=labels, right=False)
            
            avg_replies_by_length = df_with_replies.groupby('length_range')['total_replay_num'].mean()
            print(f"\n不同长度区间的平均回复数:")
            print(avg_replies_by_length)
            analysis_results['avg_replies_by_length'] = avg_replies_by_length.to_dict()
    
    # 4.8 热门游戏讨论关键词提取
    print("\n=== 热门游戏讨论关键词分析 ===")
    import jieba
    
    # 合并所有帖子标题和描述
    all_text = ' '.join(df_contents.apply(lambda row: f"{row.get('title', '')} {row.get('desc', '')}", axis=1))
    
    # 分词
    words = jieba.cut(all_text)
    
    # 过滤停用词和非中文词汇
    stopwords = ['的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '们', '来', '给', '之', '得', '以']
    filtered_words = []
    for word in words:
        if len(word) > 1 and word not in stopwords and all('\u4e00' <= char <= '\u9fff' for char in word):
            filtered_words.append(word)
    
    # 统计词频
    word_counts = Counter(filtered_words)
    top_words = word_counts.most_common(20)
    print("\n热门游戏讨论关键词TOP20：")
    for word, count in top_words:
        print(f"{word}: {count}次")
    
    analysis_results['top_game_keywords'] = top_words
    
    # 4.9 发布时间与回复数量关系分析
    print("\n=== 发布时间与回复数量关系分析 ===")
    if 'total_replay_num' in df_contents.columns and 'publish_time' in df_contents.columns:
        # 按小时和星期几分析
        df_time_replies = df_contents[['publish_time', 'total_replay_num']].dropna()
        df_time_replies['publish_hour'] = df_time_replies['publish_time'].dt.hour
        df_time_replies['publish_dayofweek'] = df_time_replies['publish_time'].dt.dayofweek
        
        # 按小时统计平均回复数
        avg_replies_by_hour = df_time_replies.groupby('publish_hour')['total_replay_num'].mean()
        print("\n不同发布小时的平均回复数：")
        print(avg_replies_by_hour.round(2))
        
        # 按星期几统计平均回复数
        avg_replies_by_day = df_time_replies.groupby('publish_dayofweek')['total_replay_num'].mean()
        day_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        avg_replies_by_day.index = day_names
        print("\n不同星期几的平均回复数：")
        print(avg_replies_by_day.round(2))
        
        analysis_results['avg_replies_by_hour'] = avg_replies_by_hour.to_dict()
        analysis_results['avg_replies_by_day'] = avg_replies_by_day.to_dict()
    
    # 4.10 游戏类型与回复数关系分析
    print("\n=== 游戏类型与回复数关系分析 ===")
    if 'total_replay_num' in df_contents.columns and 'game_type' in df_contents.columns:
        avg_replies_by_type = df_contents.groupby('game_type')['total_replay_num'].mean()
        print("\n不同游戏类型的平均回复数：")
        print(avg_replies_by_type.round(2))
        
        analysis_results['avg_replies_by_type'] = avg_replies_by_type.to_dict()
    
    # 4.11 增强版情感分析
    print("\n=== 增强版游戏评价情感分析 ===")
    # 细化情感关键词
    sentiment_keywords = {
        '非常正面': ['神作', '惊艳', '完美', '极致', '必玩', '经典', '史诗', '震撼', '爽到', '无敌'],
        '正面': ['好玩', '不错', '喜欢', '推荐', '优秀', '给力', '良心', '精彩', '流畅', '满意'],
        '中性': ['一般', '普通', '还行', '中规中矩', '过得去', '没感觉'],
        '负面': ['失望', '差评', '垃圾', '坑', '骗钱', '卡顿', '闪退', '无聊', '后悔', '卸载'],
        '非常负面': ['垃圾中的垃圾', '完全失望', '骗钱游戏', '根本没法玩', '史上最差', '烂作']
    }
    
    # 计算情感分布
    sentiment_counts = Counter()
    total_sentiment = 0
    
    for index, row in df_contents.iterrows():
        text = f"{row.get('title', '')} {row.get('desc', '')}"
        sentiment = '中性'
        
        # 检查非常负面
        if any(neg in text for neg in sentiment_keywords['非常负面']):
            sentiment = '非常负面'
        # 检查非常正面
        elif any(pos in text for pos in sentiment_keywords['非常正面']):
            sentiment = '非常正面'
        # 检查负面
        elif any(neg in text for neg in sentiment_keywords['负面']):
            sentiment = '负面'
        # 检查正面
        elif any(pos in text for pos in sentiment_keywords['正面']):
            sentiment = '正面'
        
        sentiment_counts[sentiment] += 1
        total_sentiment += 1
    
    print("\n游戏评价情感倾向分布：")
    for sentiment, count in sentiment_counts.items():
        percentage = (count / total_sentiment) * 100
        print(f"{sentiment}: {count}次 ({percentage:.2f}%)")
    
    analysis_results['sentiment_distribution'] = sentiment_counts
    
    return analysis_results, df_contents, df_comments

# 5. 生成可视化报告
def generate_visualizations(analysis_results, df_contents):
    # 创建可视化目录
    vis_dir = 'c:\\Users\\23120\\Desktop\\贴吧\\visualizations'
    if not os.path.exists(vis_dir):
        os.makedirs(vis_dir)
    
    # 5.1 热门贴吧柱状图
    plt.figure(figsize=(12, 6))
    if 'tieba_counts' in analysis_results:
        analysis_results['tieba_counts'].plot(kind='bar')
        plt.title('热门游戏贴吧TOP10')
        plt.xlabel('贴吧名称')
        plt.ylabel('帖子数量')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(f'{vis_dir}/hot_tieba.png')
        plt.close()
    
    # 5.2 热门游戏柱状图
    plt.figure(figsize=(12, 6))
    if 'game_counts' in analysis_results:
        games, counts = zip(*analysis_results['game_counts'])
        plt.bar(games, counts, color='skyblue')
        plt.title('热门游戏TOP10', fontsize=16)
        plt.xlabel('游戏名称', fontsize=12)
        plt.ylabel('提及次数', fontsize=12)
        plt.xticks(rotation=45, ha='right', fontsize=10)
        plt.grid(True, alpha=0.3, linestyle='--', axis='y')
        plt.tight_layout()
        plt.savefig(f'{vis_dir}/hot_games.png', dpi=300)
        plt.close()
    
    # 5.2.1 主机游戏热度柱状图
    plt.figure(figsize=(12, 6))
    if 'host_game_counts' in analysis_results and analysis_results['host_game_counts']:
        # 过滤掉[主机平台内容]项
        filtered_host = [(game, count) for game, count in analysis_results['host_game_counts'] if game != '[主机平台内容]']
        if filtered_host:
            host_games, host_counts = zip(*filtered_host)
            plt.bar(host_games, host_counts, color='#4CAF50')
            plt.title('主机游戏热度TOP10', fontsize=16)
            plt.xlabel('游戏名称', fontsize=12)
            plt.ylabel('提及次数', fontsize=12)
            plt.xticks(rotation=45, ha='right', fontsize=10)
            plt.grid(True, alpha=0.3, linestyle='--', axis='y')
            plt.tight_layout()
            plt.savefig(f'{vis_dir}/hot_host_games.png', dpi=300)
    plt.close()
    
    # 5.2.2 手游热度柱状图
    plt.figure(figsize=(12, 6))
    if 'mobile_game_counts' in analysis_results and analysis_results['mobile_game_counts']:
        # 过滤掉[手游平台内容]项
        filtered_mobile = [(game, count) for game, count in analysis_results['mobile_game_counts'] if game != '[手游平台内容]']
        if filtered_mobile:
            mobile_games, mobile_counts = zip(*filtered_mobile)
            plt.bar(mobile_games, mobile_counts, color='#2196F3')
            plt.title('手游热度TOP10', fontsize=16)
            plt.xlabel('游戏名称', fontsize=12)
            plt.ylabel('提及次数', fontsize=12)
            plt.xticks(rotation=45, ha='right', fontsize=10)
            plt.grid(True, alpha=0.3, linestyle='--', axis='y')
            plt.tight_layout()
            plt.savefig(f'{vis_dir}/hot_mobile_games.png', dpi=300)
    plt.close()
    
    # 5.3 发布时间趋势图
    plt.figure(figsize=(14, 8))
    if 'daily_posts' in analysis_results:
        daily_posts = analysis_results['daily_posts']
        
        # 创建临时DataFrame并将索引转换为DatetimeIndex
        temp_df = pd.DataFrame({'count': daily_posts})
        temp_df.index = pd.to_datetime(temp_df.index)
        
        # 过滤2025-2026年的数据
        mask = (temp_df.index >= '2025-01-01') & (temp_df.index <= '2026-12-31')
        filtered_daily_posts = temp_df[mask]
        
        if not filtered_daily_posts.empty:
            # 创建折线图
            ax = filtered_daily_posts['count'].plot(kind='line', marker='o', linewidth=2, markersize=6)
            
            plt.title('帖子发布时间趋势 (2025-2026)', fontsize=16)
            plt.xlabel('日期', fontsize=12)
            plt.ylabel('帖子数量', fontsize=12)
            
            # 优化日期显示
            plt.xticks(rotation=45, ha='right', fontsize=10)
            
            # 添加更密集的网格线
            plt.grid(True, alpha=0.3, linestyle='--')
            
            # 标注数据集中的时间段
            plt.axvspan('2025-11-13', '2025-11-17', alpha=0.2, color='yellow', label='2025年11月中旬集中期')
            plt.axvspan('2025-12-23', '2025-12-25', alpha=0.2, color='red', label='2025年12月下旬集中期')
            
            # 添加图例
            plt.legend()
            
            plt.tight_layout()
            plt.savefig(f'{vis_dir}/post_trend.png', dpi=300)
        plt.close()
        
        # 生成月份聚合的柱状图
        plt.figure(figsize=(12, 6))
        if not filtered_daily_posts.empty:
            # 按月聚合
            monthly_posts = filtered_daily_posts.resample('ME').sum()
            monthly_posts.plot(kind='bar', color='skyblue', use_index=True)
            plt.title('帖子发布月份分布 (2025-2026)', fontsize=16)
            plt.xlabel('月份', fontsize=12)
            plt.ylabel('帖子数量', fontsize=12)
            plt.xticks(rotation=45, ha='right', fontsize=10)
            plt.grid(True, alpha=0.3, linestyle='--', axis='y')
            plt.tight_layout()
            plt.savefig(f'{vis_dir}/monthly_distribution.png', dpi=300)
        plt.close()
    
    # 5.4 好评率饼图
    plt.figure(figsize=(8, 8))
    if 'sentiment_stats' in analysis_results:
        sentiment = analysis_results['sentiment_stats']
        labels = ['好评', '差评', '中性']
        sizes = [sentiment['positive_rate'], sentiment['negative_rate'], sentiment['neutral_rate']]
        colors = ['#4CAF50', '#F44336', '#9E9E9E']
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        plt.title('游戏评价分布')
        plt.axis('equal')
        plt.tight_layout()
        plt.savefig(f'{vis_dir}/sentiment_pie.png')
        plt.close()
    
    # 5.5 回复数分布直方图
    plt.figure(figsize=(12, 6))
    if 'total_replay_num' in df_contents.columns:
        # 过滤掉回复数为0的帖子，只显示有回复的
        filtered_replies = df_contents[df_contents['total_replay_num'] > 0]['total_replay_num']
        plt.hist(filtered_replies, bins=20, edgecolor='black')
        plt.title('帖子回复数分布')
        plt.xlabel('回复数')
        plt.ylabel('帖子数量')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(f'{vis_dir}/replies_distribution.png')
        plt.close()
    
    # 5.6 双平台游戏分析图
    plt.figure(figsize=(12, 6))
    if 'cross_platform_games' in analysis_results and analysis_results['cross_platform_games']:
        cross_games = analysis_results['cross_platform_games']
        
        # 从分析结果中获取主机和手游游戏计数
        host_game_dict = dict(analysis_results['host_game_counts'])
        mobile_game_dict = dict(analysis_results['mobile_game_counts'])
        
        host_counts = [host_game_dict[game] for game in cross_games]
        mobile_counts = [mobile_game_dict[game] for game in cross_games]
        
        x = range(len(cross_games))
        width = 0.35
        
        plt.bar([i - width/2 for i in x], host_counts, width, label='主机平台', color='#4CAF50')
        plt.bar([i + width/2 for i in x], mobile_counts, width, label='手游平台', color='#2196F3')
        
        plt.title('双平台游戏热度对比', fontsize=16)
        plt.xlabel('游戏名称', fontsize=12)
        plt.ylabel('提及次数', fontsize=12)
        plt.xticks(x, cross_games, rotation=45, ha='right', fontsize=10)
        plt.legend()
        plt.grid(True, alpha=0.3, linestyle='--', axis='y')
        plt.tight_layout()
        plt.savefig(f'{vis_dir}/cross_platform_games.png', dpi=300)
        plt.close()
    
    # 5.7 游戏类型时间趋势图
    plt.figure(figsize=(14, 8))
    if 'monthly_type_counts' in analysis_results and not analysis_results['monthly_type_counts'].empty:
        monthly_counts = analysis_results['monthly_type_counts']
        monthly_counts.plot(kind='line', marker='o', linewidth=2, markersize=6)
        
        plt.title('不同游戏类型的月度分布趋势', fontsize=16)
        plt.xlabel('月份', fontsize=12)
        plt.ylabel('帖子数量', fontsize=12)
        plt.xticks(rotation=45, ha='right', fontsize=10)
        plt.grid(True, alpha=0.3, linestyle='--')
        plt.legend()
        plt.tight_layout()
        plt.savefig(f'{vis_dir}/game_type_trend.png', dpi=300)
        plt.close()
    
    # 5.8 游戏类型分布饼图
    plt.figure(figsize=(8, 8))
    if 'game_type_distribution' in analysis_results:
        game_types = pd.Series(analysis_results['game_type_distribution'])
        game_types.plot(kind='pie', autopct='%1.1f%%', startangle=90)
        plt.title('游戏类型分布', fontsize=16)
        plt.axis('equal')
        plt.legend(title='游戏类型')
        plt.tight_layout()
        plt.savefig(f'{vis_dir}/game_type_distribution.png', dpi=300)
        plt.close()
    
    # 5.9 帖子长度与回复数关系图
    plt.figure(figsize=(12, 6))
    if 'post_length' in df_contents.columns:
        # 只分析有回复的帖子
        df_with_replies = df_contents[df_contents['total_replay_num'] > 0]
        if len(df_with_replies) > 0:
            plt.scatter(df_with_replies['post_length'], df_with_replies['total_replay_num'], alpha=0.5)
            plt.title('帖子长度与回复数关系', fontsize=16)
            plt.xlabel('帖子长度（字符数）', fontsize=12)
            plt.ylabel('回复数', fontsize=12)
            plt.grid(True, alpha=0.3, linestyle='--')
            plt.tight_layout()
            plt.savefig(f'{vis_dir}/length_reply_scatter.png', dpi=300)
            plt.close()
    
    # 5.10 不同长度区间平均回复数图
    plt.figure(figsize=(12, 6))
    if 'avg_replies_by_length' in analysis_results:
        avg_replies = pd.Series(analysis_results['avg_replies_by_length'])
        avg_replies.plot(kind='bar', color='skyblue', edgecolor='black')
        plt.title('不同帖子长度区间的平均回复数', fontsize=16)
        plt.xlabel('帖子长度区间', fontsize=12)
        plt.ylabel('平均回复数', fontsize=12)
        plt.xticks(rotation=45, ha='right', fontsize=10)
        plt.grid(True, alpha=0.3, linestyle='--', axis='y')
        
        # 添加数据标签
        for i, v in enumerate(avg_replies):
            plt.text(i, v + 0.5, f'{v:.1f}', ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        plt.savefig(f'{vis_dir}/avg_replies_by_length.png', dpi=300)
        plt.close()
    
    # 5.11 评论最多的帖子TOP10
    plt.figure(figsize=(12, 8))
    if 'comments_per_post' in analysis_results:
        comments_dict = analysis_results['comments_per_post']
        if comments_dict:
            # 转换为Series并排序
            comments_series = pd.Series(comments_dict)
            top_commented = comments_series.head(10).sort_values(ascending=True)
            
            top_commented.plot(kind='barh', color='purple', edgecolor='black')
            plt.title('评论最多的帖子TOP10', fontsize=16)
            plt.xlabel('评论数量', fontsize=12)
            plt.ylabel('帖子标题', fontsize=12)
            plt.grid(True, alpha=0.3, linestyle='--', axis='x')
            
            # 获取帖子标题
            yticks = []
            for note_id in top_commented.index:
                post_title = df_contents[df_contents['note_id'] == note_id]['title'].values[0] if len(df_contents[df_contents['note_id'] == note_id]) > 0 else '未知标题'
                yticks.append(post_title[:25] + '...')
            
            plt.yticks(range(len(yticks)), yticks, fontsize=10)
            
            # 添加数据标签
            for i, v in enumerate(top_commented):
                plt.text(v + 0.5, i, str(v), va='center', fontsize=10)
            
            plt.tight_layout()
            plt.savefig(f'{vis_dir}/top_commented_posts.png', dpi=300)
            plt.close()
    
    # 5.12 热门游戏讨论关键词TOP20
    plt.figure(figsize=(14, 8))
    if 'top_game_keywords' in analysis_results:
        words, counts = zip(*analysis_results['top_game_keywords'])
        plt.barh(words, counts, color='skyblue', edgecolor='black')
        plt.title('热门游戏讨论关键词TOP20', fontsize=16)
        plt.xlabel('提及次数', fontsize=12)
        plt.ylabel('关键词', fontsize=12)
        plt.grid(True, alpha=0.3, linestyle='--', axis='x')
        
        # 调整字体大小和间距
        plt.yticks(fontsize=10)
        plt.xlim(0, max(counts) * 1.1)
        
        # 添加数据标签
        for i, v in enumerate(counts):
            plt.text(v + 0.5, i, str(v), va='center', fontsize=10)
        
        plt.tight_layout()
        plt.savefig(f'{vis_dir}/top_game_keywords.png', dpi=300)
        plt.close()
    
    # 5.13 发布时间与回复数量关系
    # 按小时
    plt.figure(figsize=(12, 6))
    if 'avg_replies_by_hour' in analysis_results:
        avg_replies = pd.Series(analysis_results['avg_replies_by_hour'])
        avg_replies.plot(kind='bar', color='orange', edgecolor='black')
        plt.title('不同发布小时的平均回复数', fontsize=16)
        plt.xlabel('发布小时', fontsize=12)
        plt.ylabel('平均回复数', fontsize=12)
        plt.xticks(fontsize=10)
        plt.grid(True, alpha=0.3, linestyle='--', axis='y')
        plt.tight_layout()
        plt.savefig(f'{vis_dir}/avg_replies_by_hour.png', dpi=300)
        plt.close()
    
    # 按星期几
    plt.figure(figsize=(12, 6))
    if 'avg_replies_by_day' in analysis_results:
        avg_replies = pd.Series(analysis_results['avg_replies_by_day'])
        avg_replies.plot(kind='bar', color='green', edgecolor='black')
        plt.title('不同星期几的平均回复数', fontsize=16)
        plt.xlabel('星期几', fontsize=12)
        plt.ylabel('平均回复数', fontsize=12)
        plt.xticks(fontsize=10)
        plt.grid(True, alpha=0.3, linestyle='--', axis='y')
        
        # 添加数据标签
        for i, v in enumerate(avg_replies):
            plt.text(i, v + 0.5, f'{v:.1f}', ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        plt.savefig(f'{vis_dir}/avg_replies_by_day.png', dpi=300)
        plt.close()
    
    # 5.14 不同游戏类型的平均回复数
    plt.figure(figsize=(12, 6))
    if 'avg_replies_by_type' in analysis_results:
        avg_replies = pd.Series(analysis_results['avg_replies_by_type'])
        avg_replies.plot(kind='bar', color=['blue', 'red', 'green', 'purple'], edgecolor='black')
        plt.title('不同游戏类型的平均回复数', fontsize=16)
        plt.xlabel('游戏类型', fontsize=12)
        plt.ylabel('平均回复数', fontsize=12)
        plt.xticks(fontsize=10)
        plt.grid(True, alpha=0.3, linestyle='--', axis='y')
        
        # 添加数据标签
        for i, v in enumerate(avg_replies):
            plt.text(i, v + 0.5, f'{v:.1f}', ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        plt.savefig(f'{vis_dir}/avg_replies_by_type.png', dpi=300)
        plt.close()
    
    # 5.15 增强版情感分析分布
    plt.figure(figsize=(8, 8))
    if 'sentiment_distribution' in analysis_results:
        sentiment = analysis_results['sentiment_distribution']
        if sentiment:
            labels = list(sentiment.keys())
            sizes = list(sentiment.values())
            colors = ['#4CAF50', '#8BC34A', '#FFC107', '#FF5722', '#F44336']
            plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            plt.title('游戏评价情感倾向分布（增强版）', fontsize=16)
            plt.axis('equal')
            plt.legend(title='情感倾向')
            plt.tight_layout()
            plt.savefig(f'{vis_dir}/enhanced_sentiment_pie.png', dpi=300)
            plt.close()
    
    print(f"\n可视化报告已生成，保存在 {vis_dir} 目录中")

# 主函数
def main():
    print("正在加载数据...")
    contents, comments = load_all_data()
    
    print(f"原始数据：{len(contents)}个帖子，{len(comments)}条评论")
    
    print("\n正在筛选游戏相关内容...")
    filtered_contents = filter_game_related(contents)
    filtered_comments = filter_game_related(comments)
    
    print(f"筛选后：{len(filtered_contents)}个帖子，{len(filtered_comments)}条评论")
    
    print("\n正在去重...")
    unique_contents = remove_duplicates(filtered_contents)
    unique_comments = remove_duplicates(filtered_comments)
    
    print(f"去重后：{len(unique_contents)}个帖子，{len(unique_comments)}条评论")
    
    print("\n正在分析数据...")
    analysis_results, df_contents, df_comments = analyze_data(unique_contents, unique_comments)
    
    print("\n正在生成可视化报告...")
    generate_visualizations(analysis_results, df_contents)
    
    # 保存处理后的数据
    output_dir = 'c:\\Users\\23120\\Desktop\\贴吧\\processed_data'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    with open(f'{output_dir}/filtered_contents.json', 'w', encoding='utf-8') as f:
        json.dump(unique_contents, f, ensure_ascii=False, indent=2)
    
    with open(f'{output_dir}/filtered_comments.json', 'w', encoding='utf-8') as f:
        json.dump(unique_comments, f, ensure_ascii=False, indent=2)
    
    print(f"\n处理后的数据已保存到 {output_dir} 目录")
    print("\n数据分析完成！")

if __name__ == "__main__":
    main()
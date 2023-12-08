import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import math
import pandas as pd

df = pd.read_csv("wechat.csv")  # 请将此路径替换为您的文件路径
# 确保日期列是日期时间格式
df["日期"] = pd.to_datetime(df["日期"])


# 获取年份选项
years = df["日期"].dt.year.unique()
year_options = [{"label": str(year), "value": year} for year in years]

# 初始化 Dash 应用
app = dash.Dash(__name__)

server=app.server

# 定义可选的数据系列
options = [
    {"label": "阅读次数", "value": "阅读次数"},
    {"label": "阅读人数", "value": "阅读人数"},
    {"label": "分享次数", "value": "分享次数"},
    {"label": "分享人数", "value": "分享人数"},
    {"label": "阅读原文次数", "value": "阅读原文次数"},
    {"label": "阅读原文人数", "value": "阅读原文人数"},
    {"label": "收藏次数", "value": "收藏次数"},
    {"label": "收藏人数", "value": "收藏人数"},
    {"label": "群发篇数", "value": "群发篇数"},
]


# 定义应用布局
app.layout = html.Div(
    [
        html.H1("图灵大会微信公众号数据分析"),
        dcc.Dropdown(
            id="data-select",
            options=options,
            value=["阅读次数", "阅读人数"],  # 默认选中的项
            multi=True,
        ),
        dcc.Graph(id="graph-output"),
        dcc.Dropdown(
            id="year-select",
            options=year_options,
            value=years[0],  # 默认选中的年份
        ),
        dcc.Graph(id="heatmap-output"),

    ],
    style={"max-width": "900px", "margin": "0 auto"},
)


# 回调函数来更新图表
@app.callback(Output("graph-output", "figure"), [Input("data-select", "value")])
def update_graph(selected_data):
    traces = []
    for data in selected_data:
        traces.append(go.Scatter(x=df["日期"], y=df[data], mode="lines", name=data))

    return {
        "data": traces,
        "layout": go.Layout(
            xaxis={"title": "日期"},
            yaxis={"title": "数据"},
            height=300,
            margin=dict(l=50, r=50, t=50, b=50),
        ),
    }


# 回调函数来更新热力图
@app.callback(
    Output("heatmap-output", "figure"),
    [Input("year-select", "value"), Input("data-select", "value")],
)
def update_heatmap(selected_year, selected_data):
    # 筛选出选择的年份
    filtered_df = df[df["日期"].dt.year == selected_year]

    # 准备热力图数据，初始化一个空的矩阵，每一行代表一周的某一天
    heatmap_data = [[0 for _ in range(53)] for _ in range(7)]  # 53周，每周7天
    text_data = [["" for _ in range(53)] for _ in range(7)]  # 文本矩阵，用于悬停信息

    # 填充热力图数据
    for index, row in filtered_df.iterrows():
        weekday = row["日期"].weekday()  # Monday=0, Sunday=6
        week_of_year = row["日期"].isocalendar()[1]  # 获取年中的周数
        # 为热力图数据填充值
        heatmap_data[weekday][week_of_year - 1] = math.log10(
            row[selected_data].sum() + 1
        )
        # 为文本数据填充日期和数值
        date_str = row["日期"].strftime("%Y-%m-%d")
        info = f"{date_str}<br>"
        for data in selected_data:
            info += f"{data}: {row[data]}<br>"
        text_data[weekday][week_of_year - 1] = info

    # 填充没有数据的天数为0
    for week in range(53):
        for day in range(7):
            if heatmap_data[day][week] is None:
                heatmap_data[day][week] = 0

    # 生成热力图
    trace = go.Heatmap(
        z=heatmap_data,
        x=list(range(53)),  # 周数从1到53
        y=list(range(7)),
        zmin=0,
        zmax=5,
        text=text_data,  # 设置文本数据
        hoverinfo="text",  # 悬停时只显示文本
        colorscale="Blues",
        showscale=True,
        colorbar=dict(tickvals=[]),
    )

    # 返回热力图
    return {
        "data": [trace],
        "layout": go.Layout(
            title=f"{selected_year}年 {selected_data} 活跃度热力图",
            xaxis=dict(
                tickmode="array",
                tickvals=[],
                fixedrange=True,
                showgrid=False,
            ),
            yaxis=dict(
                tickmode="array",
                tickvals=list(range(7)),
                ticktext=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
                fixedrange=True,
                showgrid=False,
                # scaleanchor="x",
                # scaleratio=1,
            ),
            margin=dict(l=50, r=50, t=50, b=50),
            height=300,
        ),
    }


# 运行应用
if __name__ == "__main__":
    app.run_server(debug=True)

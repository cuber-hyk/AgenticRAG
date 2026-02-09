# 滑雪数据分析代码

以下是使用 Python 分析滑雪速度的示例代码：

```python
import pandas as pd
import matplotlib.pyplot as plt

def analyze_speed(data_file):
    df = pd.read_csv(data_file)
    avg_speed = df['speed'].mean()
    max_speed = df['speed'].max()
    
    print(f"平均速度: {avg_speed} km/h")
    print(f"最大速度: {max_speed} km/h")
    
    plt.plot(df['time'], df['speed'])
    plt.title("Skiing Speed Over Time")
    plt.show()

# 使用示例
analyze_speed('ski_session_01.csv')
```

该代码可以帮助运动员优化滑行策略。

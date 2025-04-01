# 导入必要的库
import logging  # 日志记录模块
from gouji.core import GoujiGame  # 导入主游戏类
from gouji.core import DefaultAITurnHandler  # 导入默认AI回合处理器
from gouji.core import HumanPlayerTurnHandler  # 导入人类玩家回合处理器
from gouji.ai import DQNTurnHandler  # 导入DQN AI回合处理器
from gouji.ai import DQNTrainer  # 导入DQN训练器
from gouji.components import GameStateComponent  # 导入游戏状态组件

if __name__ == "__main__":
    # 程序主入口点 - DQN训练模式

    # 配置日志系统
    logging.basicConfig(
        level=logging.INFO,  # 设置日志级别为INFO，低于此级别的日志不会显示
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # 设置日志格式
        filename="logs/debug.log",  # 将日志输出到文件
    )

    # 创建DQN训练器实例，设置训练回合数为10000
    trainer = DQNTrainer(num_episodes=2000)

    # 开始DQN训练过程
    logging.info("开始DQN训练...")
    trainer.train()

    # 训练完成后，保存每个DQN处理器的模型
    handlers = trainer.get_dqn_handlers()  # 获取所有DQN处理器
    for player_id, handler in handlers.items():
        # 为每个玩家保存训练好的模型，文件名包含玩家ID
        handler.save_model(f"models/dqn_player{player_id}_final.pt")

    # 对训练好的模型进行评估，进行30局游戏测试
    logging.info("开始评估模型...")
    trainer.evaluate(num_games=10)

    # 使用训练好的模型进行一局演示游戏
    logging.info("\n使用训练好的模型进行一局游戏演示...")
    # 注意：这里原有的演示代码被注释掉了，需要实现时可以取消注释

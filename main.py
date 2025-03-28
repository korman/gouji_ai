import esper
import logging
from gouji.core import GoujiGame
from gouji.core import DefaultAITurnHandler
from gouji.core import HumanPlayerTurnHandler
from gouji.ai import DQNTurnHandler
from gouji.ai import DQNTrainer
from gouji.components import GameStateComponent

if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        filename="logs/debug.log",
    )

    trainer = DQNTrainer(num_episodes=10000)

    logging.info("开始DQN训练...")
    trainer.train()

    handlers = trainer.get_dqn_handlers()
    for player_id, handler in handlers.items():
        handler.save_model(f"models/dqn_player{player_id}_final.pt")

    logging.info("开始评估模型...")
    trainer.evaluate(num_games=30)

    logging.info("\n使用训练好的模型进行一局游戏演示...")

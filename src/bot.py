from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
from rlbot.utils.structures.quick_chats import QuickChats

import math
# import debug
import logging

logger = logging.getLogger(__name__)

def get_game_score(packet: GameTickPacket):
    score = [0, 0] # Orange Team Is Index 0, Blue Team Is Index 1

    for car in packet.game_cars:
        score[car.team] += car.score_info.goals

    return score

def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

class MyBot(BaseAgent):
    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.controller = SimpleControllerState()

        print("RL-CrypticBot : Loaded!")

        # Game Data
        self.bot_pos = None
        self.bot_rot = None

        # Dodging
        # self.DODGE_TIME = 3
        # self.should_dodge = False
        # self.on_second_jump = False
        # self.next_dodge_time = 0
        # self.dodge_interval = 0

        # # Distance To Dodge Ball
        # self.DISTANCE_TO_DODGE = 1000

        self.DISTANCE_FROM_BALL_TO_BOOST = 1500
        self.POWERSLIDE_ANGLE = 3

    def initialize_agent(self):
        self.previous_frame_opponent_score = 0
    
    def aim(self, target_x, target_y):
        angle_between_bot_and_target = math.atan2(target_y - self.bot_pos.y, target_x - self.bot_pos.x)
        angle_front_to_target = angle_between_bot_and_target - self.bot_yaw

        self.controller.handbrake = abs(angle_front_to_target) > self.POWERSLIDE_ANGLE

        if angle_front_to_target < -math.pi:
            angle_front_to_target += 2 * math.pi
        if angle_front_to_target > math.pi:
            angle_front_to_target -= 2 * math.pi

        if angle_front_to_target < math.radians(-10):
            self.controller.steer = -1
        elif angle_front_to_target > math.radians(10):
            self.controller.steer = 1
        else:
            self.controller.steer = 0

    # def check_for_dodge(self):
    #     if self.should_dodge and time.time() > self.next_dodge_time:
    #         self.controller.jump = True
    #         self.controller.pitch = -1

    #         if self.on_second_jump:
    #             self.on_second_jump = False
    #             self.should_dodge = False
    #         else:
    #             self.on_second_jump = True
    #             self.should_dodge = time.time() + self.DODGE_TIME

    def handle_quick_chat(self, index, team, quick_chat):
        if team != self.team and quick_chat == QuickChats.Compliments_NiceShot:
            self.send_quick_chat(QuickChats.CHAT_EVERYONE, QuickChats.Custom_Excuses_Rigged)

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        self.bot_yaw = packet.game_cars[self.team].physics.rotation.yaw
        self.bot_pos = packet.game_cars[self.index].physics.location
        
        ball_pos = packet.game_ball.physics.location
        self.controller.throttle = 1

        self.controller.boost = distance(self.bot_pos.x, self.bot_pos.y, ball_pos.x, ball_pos.y) > self.DISTANCE_FROM_BALL_TO_BOOST

        if ball_pos.x == 0 and ball_pos.y == 0:
            self.aim(ball_pos.x, ball_pos.y)
            self.controller.boost = True

        # if (self.team == 0 and self.bot_pos.y < ball_pos.y) or (self.team == 1 and self.bot_pos.y > ball_pos.y):
        #     self.aim(ball_pos.x, ball_pos.y)
        #     if distance(self.bot_pos.x, self.bot_pos.y, ball_pos.x, ball_pos.y) < self.DISTANCE_TO_DODGE:
        #         self.should_dodge = True
        # else:
        #     if self.team == 0:
        #         self.aim(0, -5000) # Blue's Goal Is Located At 0, -5000
        #     elif self.team == 1:
        #         self.aim(0, 5000) # Orange's Goal Is Located At 0, 5000

        self.controller.jump = 0
        # self.check_for_dodge()

        # Cryptic QuickChats
        current_score = get_game_score(packet)
        if self.previous_frame_opponent_score < current_score[not self.team]:
            self.send_quick_chat(QuickChats.CHAT_EVERYONE, QuickChats.Compliments_NiceShot)

        self.previous_frame_opponent_score = current_score[not self.team]

        # corner_debug = "Cryptic Debugging :\n"
        # corner_debug += "Game Time Remaining : {}\n".format(packet.game_info.game_time_remaining)
        # cryptic_debug(self.renderer, corner_debug)

        return self.controller

        # renderer.begin_rendering()

        # if corner_debug:
        #     corner_display_y = 900 - (corner_debug.count('\n') * 20)
        #     renderer.draw_string_2d(10, corner_display_y, 1, 1, corner_debug, renderer.white())

        # renderer.end_rendering()
        # ball_prediction = self.get_ball_prediction_struct()

        # if ball_prediction is not None: # Just Prints All Predicted Locations Of Were The Ball Goes
        #     for i in range(0, ball_prediction.num_slices):
        #         prediction_slice = ball_prediction.slices[i]
        #         location = prediction_slice.physics.location
        #         self.logger.info(f"At Time {prediction_slice.game_seconds}, The Ball Will Be At ({location.x}. {location.y}, {location.z})")
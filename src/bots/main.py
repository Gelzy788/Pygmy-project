import pygame as pg
import json
from ray_cast.render_ray import setup, render_ray
from ray_cast.particle import Particle
from ray_cast.ray import Ray
from set_path.set_paths import set_path

# paths = {
#     "object_1": [
#         (30, 60), (31, 61), (32, 62), (33, 63), (34, 64), (35, 65), (36, 66), (37, 67), (38, 68), (39, 69),
#         (40, 70), (41, 71), (42, 72), (43, 73), (44, 74), (45, 75), (46, 76), (47, 77), (48, 78), (49, 79),
#         (50, 80), (51, 81), (52, 82), (53, 83), (54, 84), (55, 85), (56, 86), (57, 87), (58, 88), (59, 89),
#         (60, 90), (61, 91), (62, 92), (63, 93), (64, 94), (65, 95), (66, 96), (67, 97), (68, 98), (69, 99),
#         (70, 100), (71, 101), (72, 102), (73, 103), (74, 104), (75, 105), (76, 106), (77, 107), (78, 108),
#         (79, 109), (80, 110), (81, 111), (82, 112), (83, 113), (84, 114), (85, 115), (86, 116), (87, 117),
#         (88, 118), (89, 119), (90, 120), (91, 121), (92, 122), (93, 123), (94, 124), (95, 125), (96, 126),
#         (97, 127), (98, 128), (99, 129), (100, 130), (101, 131), (102, 132), (103, 133), (104, 134), (105, 135),
#         (106, 136), (107, 137), (108, 138), (109, 139), (110, 140), (111, 141), (112, 142), (113, 143), (114, 144),
#         (115, 145), (116, 146), (117, 147), (118, 148), (119, 149), (120, 150), (121, 151), (122, 152), (123, 153),
#         (124, 154), (125, 155), (126, 156), (127, 157), (128, 158), (129, 159), (130, 160), (131, 161), (132, 162),
#         (133, 163), (134, 164), (135, 165), (136, 166), (137, 167), (138, 168), (139, 169), (140, 170), (141, 171),
#         (142, 172), (143, 173), (144, 174), (145, 175), (146, 176), (147, 177), (148, 178), (149, 179), (150, 180),
#         (151, 181), (152, 182), (153, 183), (154, 184), (155, 185), (156, 186), (157, 187), (158, 188), (159, 189),
#         (160, 190), (161, 191), (162, 192), (163, 193), (164, 194), (165, 195), (166, 196), (167, 197), (168, 198),
#         (169, 199), (170, 200), (171, 201), (172, 202), (173, 203), (174, 204), (175, 205), (176, 206), (177, 207),
#         (178, 208), (179, 209), (180, 210), (181, 211), (182, 212), (183, 213), (184, 214), (185, 215), (186, 216),
#         (187, 217), (188, 218), (189, 219), (190, 220), (191, 221), (192, 222), (193, 223), (194, 224), (195, 225),
#         (196, 226), (197, 227), (198, 228), (199, 229), (200, 230), (201, 231), (202, 232), (203, 233), (204, 234),
#         (205, 235), (206, 236), (207, 237), (208, 238), (209, 239), (210, 240)
#     ],
#     "object_2": [
#         (100, 200), (101, 201), (102, 202), (103, 203), (104, 204), (105, 205), (106, 206), (107, 207),
#         (108, 208), (109, 209), (110, 210), (111, 211), (112, 212), (113, 213), (114, 214), (115, 215),
#         (116, 216), (117, 217), (118, 218), (119, 219), (120, 220), (121, 221), (122, 222), (123, 223),
#         (124, 224), (125, 225), (126, 226), (127, 227), (128, 228), (129, 229), (130, 230), (131, 231),
#         (132, 232), (133, 233), (134, 234), (135, 235), (136, 236), (137, 237), (138, 238), (139, 239),
#         (140, 240), (141, 241), (142, 242), (143, 243), (144, 244), (145, 245), (146, 246), (147, 247),
#         (148, 248), (149, 249), (150, 250), (151, 251), (152, 252), (153, 253), (154, 254), (155, 255),
#         (156, 256), (157, 257), (158, 258), (159, 259), (160, 260), (161, 261), (162, 262), (163, 263),
#         (164, 264), (165, 265), (166, 266), (167, 267), (168, 268), (169, 269), (170, 270), (171, 271),
#         (172, 272), (173, 273), (174, 274), (175, 275), (176, 276), (177, 277), (178, 278), (179, 279),
#         (180, 280), (181, 281), (182, 282), (183, 283), (184, 284), (185, 285), (186, 286), (187, 287),
#         (188, 288), (189, 289), (190, 290), (191, 291), (192, 292), (193, 293), (194, 294), (195, 295),
#         (196, 296), (197, 297), (198, 298), (199, 299), (200, 300), (201, 301), (202, 302), (203, 303),
#         (204, 304), (205, 305), (206, 306), (207, 307), (208, 308), (209, 309), (210, 310), (211, 311),
#         (212, 312), (213, 313), (214, 314), (215, 315), (216, 316), (217, 317), (218, 318), (219, 319),
#         (220, 320), (221, 321), (222, 322), (223, 323), (224, 324), (225, 325), (226, 326), (227, 327),
#         (228, 328), (229, 329), (230, 330), (231, 331), (232, 332), (233, 333), (234, 334), (235, 335),
#         (236, 336), (237, 337), (238, 338), (239, 339), (240, 340), (241, 341), (242, 342), (243, 343),
#         (244, 344), (245, 345), (246, 346), (247, 347), (248, 348), (249, 349), (250, 350)
#     ]
# }

# paths = {
#     "bot_1": [
#         (35, 31), (35, 33), (35, 38), (35, 42), 
#         (35, 50), (35, 59), (36, 68), (36, 81), 
#         (36, 88), (35, 96), (35, 105), (35, 110), 
#         (34, 116), (34, 120), (33, 125), (33, 126),
#         (33, 127)
#     ],
#     "bot_2": [
#     (138, 36), (138, 37), (137, 39), (137, 41),
#     (137, 42), (137, 44), (137, 47), (137, 49), 
#     (137, 50), (137, 52), (137, 54)
#     ]
#  }

def main():
    set_up = setup()
    set_path()

    particles = {}
    with open('src/bots/set_path/paths.json') as f:
        templates: dict = json.load(f)
        # print(len(templates))
    
    # Создание объектов (частицы, лучи, границы)
    for i in range(len(templates)):
        particles[f'bot_{i}'] = Particle(speed=templates[f'bot_{i}']['speed'])

    rays = {key: [Ray(p, i * -set_up[6] / set_up[3]) for i in range(set_up[3])] for key, p in particles.items()}
    boundaries = []
    paths = {
        bot: [(x, y) for x, y in data["path"]]
        for bot, data in templates.items()
    }
    # Запуск игры

    render_ray(set_up, particles, rays, boundaries, paths)

if __name__ == "__main__":
    main()
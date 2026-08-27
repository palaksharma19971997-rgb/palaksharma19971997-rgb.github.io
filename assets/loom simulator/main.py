import asyncio
import pygame


# ============================================================
#                     CONSTANTS
# ============================================================

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GREY = (120, 120, 120)
GREY = (160, 160, 160)
BROWN = (139, 69, 19)
WEFT_COLOR = (180, 255, 180)
WARP_COLOR = (0, 100, 0)
SHUTTLE_COLOR = (200, 50, 50)
HIGHLIGHT_COLOR = (255, 0, 0)
RESET_BUTTON_COLOR = (70, 130, 180)


# ============================================================
#                     LOOM VARIABLES
# ============================================================

warpA_x_orig = [220, 270, 320, 370]
warpB_x_orig = [245, 295, 345, 395]

all_warp_x_orig = warpA_x_orig + warpB_x_orig

leftmost = min(all_warp_x_orig)
rightmost = max(all_warp_x_orig)

original_width = rightmost - leftmost

offset = (
    SCREEN_WIDTH // 2
    - (original_width // 2)
    - leftmost
)

warpA_x = [x + offset for x in warpA_x_orig]
warpB_x = [x + offset for x in warpB_x_orig]

all_warp_x = warpA_x + warpB_x

warp_length = 220

frame1_width = warpA_x[-1] - warpA_x[0]
frame2_width = warpB_x[-1] - warpB_x[0]

frame_height = 20

frame1_y_orig = 200
frame2_y_orig = 200

frame1_y = frame1_y_orig
frame2_y = frame2_y_orig

lift_max = 150
lift_speed = 4


# ============================================================
#                     PEDALS
# ============================================================

pedal_width = 20
pedal_height = 100

pedal1_rect = pygame.Rect(
    warpA_x[0] - 70,
    frame2_y_orig + 150,
    pedal_width,
    pedal_height
)

pedal2_rect = pygame.Rect(
    warpB_x[-1] + 50,
    frame2_y_orig + 150,
    pedal_width,
    pedal_height
)

pedal1_pressed = False
pedal2_pressed = False

pedal1_handled = False
pedal2_handled = False

reset_rect = pygame.Rect(SCREEN_WIDTH - 130, 20, 110, 40)


# ============================================================
#                     WEFT / SHUTTLE
# ============================================================

weft_drop = 20

cycle_count = 0
total_cycles = 9

weft_speed = 4

cloth_state = [
    [None for _ in range(total_cycles)]
    for _ in range(len(all_warp_x))
]

left_x = min(all_warp_x) - 5
right_x = max(all_warp_x) + 5

weft_path = []

weft_y = (
    max(frame1_y_orig, frame2_y_orig)
    + frame_height
    + 20
)

direction = 1

shuttle_moving = False

shuttle_x = left_x
shuttle_y = weft_y

shuttle_target_x = right_x

next_frame_is_1 = True


# ============================================================
#                     MAIN LOOP
# ============================================================

async def main():

    global pedal1_pressed
    global pedal2_pressed

    global pedal1_handled
    global pedal2_handled

    global frame1_y
    global frame2_y

    global cycle_count
    global weft_y

    global shuttle_moving
    global shuttle_x
    global shuttle_y
    global shuttle_target_x

    global direction
    global next_frame_is_1

    def reset_simulation():
        global frame1_y, frame2_y
        global pedal1_pressed, pedal2_pressed
        global pedal1_handled, pedal2_handled
        global cycle_count, weft_y
        global shuttle_moving, shuttle_x, shuttle_y, shuttle_target_x
        global direction, next_frame_is_1
        global cloth_state, weft_path

        frame1_y = frame1_y_orig
        frame2_y = frame2_y_orig

        pedal1_pressed = False
        pedal2_pressed = False
        pedal1_handled = False
        pedal2_handled = False

        cycle_count = 0

        weft_y = (
            max(frame1_y_orig, frame2_y_orig)
            + frame_height
            + 20
        )

        shuttle_moving = False
        shuttle_x = left_x
        shuttle_y = weft_y
        shuttle_target_x = right_x

        direction = 1
        next_frame_is_1 = True

        cloth_state = [
            [None for _ in range(total_cycles)]
            for _ in range(len(all_warp_x))
        ]

        weft_path = []

        
    pygame.init()

   

    screen = pygame.display.set_mode(
        (SCREEN_WIDTH, SCREEN_HEIGHT)
    )

    pygame.display.set_caption(
        "Stepwise Loom Simulator - Plain Weave"
    )

    font = pygame.font.SysFont(None, 20)

    running = True

    # ========================================================
    #                     GAME LOOP
    # ========================================================

    while running:

        # ----------------------------------------------------
        # EVENTS
        # ----------------------------------------------------

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:

                if event.button == 1:

                    if pedal1_rect.collidepoint(event.pos):
                        pedal1_pressed = True

                    if pedal2_rect.collidepoint(event.pos):
                        pedal2_pressed = True

                    if reset_rect.collidepoint(event.pos):
                        reset_simulation()

            elif event.type == pygame.MOUSEBUTTONUP:

                if event.button == 1:

                    pedal1_pressed = False
                    pedal2_pressed = False


         # ANIMATE FRAMES
      

        if pedal1_pressed and frame1_y > lift_max:

            frame1_y -= lift_speed

        elif not pedal1_pressed and frame1_y < frame1_y_orig:

            frame1_y += lift_speed

        if pedal2_pressed and frame2_y > lift_max:

            frame2_y -= lift_speed

        elif not pedal2_pressed and frame2_y < frame2_y_orig:

            frame2_y += lift_speed

        frame1_lifted = frame1_y < frame1_y_orig
        frame2_lifted = frame2_y < frame2_y_orig

        # ----------------------------------------------------
        # START SHUTTLE / DUMMY CYCLE
        # ----------------------------------------------------

        if not shuttle_moving and cycle_count < total_cycles:

            if cycle_count == total_cycles - 1:

                for col, warp_x in enumerate(all_warp_x):

                    if (
                        (warp_x in warpA_x and next_frame_is_1)
                        or
                        (warp_x in warpB_x and not next_frame_is_1)
                    ):

                        cloth_state[col][cycle_count] = True

                    else:

                        cloth_state[col][cycle_count] = False

                cycle_count += 1

                next_frame_is_1 = not next_frame_is_1

            else:

                if (
                    next_frame_is_1
                    and pedal1_pressed
                    and not pedal1_handled
                    and frame1_lifted
                ):

                    shuttle_y = weft_y

                    shuttle_x = (
                        left_x
                        if direction == 1
                        else right_x
                    )

                    shuttle_target_x = (
                        right_x
                        if direction == 1
                        else left_x
                    )

                    shuttle_moving = True

                    pedal1_handled = True

                elif (
                    not next_frame_is_1
                    and pedal2_pressed
                    and not pedal2_handled
                    and frame2_lifted
                ):

                    shuttle_y = weft_y

                    shuttle_x = (
                        left_x
                        if direction == 1
                        else right_x
                    )

                    shuttle_target_x = (
                        right_x
                        if direction == 1
                        else left_x
                    )

                    shuttle_moving = True

                    pedal2_handled = True

        # ----------------------------------------------------
        # RESET PEDAL HANDLING
        # ----------------------------------------------------

        if not pedal1_pressed:
            pedal1_handled = False

        if not pedal2_pressed:
            pedal2_handled = False

        # ----------------------------------------------------
        # MOVE SHUTTLE
        # ----------------------------------------------------

        if shuttle_moving:

            if shuttle_x < shuttle_target_x:

                shuttle_x += weft_speed

                if shuttle_x > shuttle_target_x:
                    shuttle_x = shuttle_target_x

            else:

                shuttle_x -= weft_speed

                if shuttle_x < shuttle_target_x:
                    shuttle_x = shuttle_target_x

            # ------------------------------------------------
            # SHUTTLE REACHED OTHER SIDE
            # ------------------------------------------------

            if shuttle_x == shuttle_target_x:

                for col, warp_x in enumerate(all_warp_x):

                    if (
                        (warp_x in warpA_x and next_frame_is_1)
                        or
                        (warp_x in warpB_x and not next_frame_is_1)
                    ):

                        cloth_state[col][cycle_count] = True

                    else:

                        cloth_state[col][cycle_count] = False

                # ------------------------------------------------
                # ADD WEFT PATH
                # ------------------------------------------------

                if weft_path:

                    start_point = (
                        weft_path[-1][1]
                    )

                else:

                    start_point = (
                        left_x,
                        shuttle_y
                    )

                weft_path.append(
                    (
                        start_point,
                        (
                            shuttle_target_x,
                            shuttle_y
                        )
                    )
                )

                # ------------------------------------------------
                # ADD CONNECTOR
                # ------------------------------------------------

                if cycle_count < total_cycles - 2:

                    if shuttle_target_x == right_x:

                        connector_start = (
                            shuttle_target_x,
                            shuttle_y
                        )

                        connector_end = (
                            right_x + 10,
                            shuttle_y + weft_drop
                        )

                    else:

                        connector_start = (
                            shuttle_target_x,
                            shuttle_y
                        )

                        connector_end = (
                            left_x - 10,
                            shuttle_y + weft_drop
                        )

                    weft_path.append(
                        (
                            connector_start,
                            connector_end
                        )
                    )

                # ------------------------------------------------
                # NEXT WEFT ROW
                # ------------------------------------------------

                weft_y += weft_drop

                cycle_count += 1

                shuttle_moving = False

                direction *= -1

                next_frame_is_1 = not next_frame_is_1

        # ====================================================
        #                     DRAWING
        # ====================================================

        screen.fill(WHITE)

        # ----------------------------------------------------
        # PEDALS
        # ----------------------------------------------------

        pygame.draw.rect(
            screen,
            BROWN,
            pedal1_rect
        )

        pygame.draw.rect(
            screen,
            BROWN,
            pedal2_rect
        )

        if pedal1_pressed:

            pygame.draw.rect(
                screen,
                HIGHLIGHT_COLOR,
                pedal1_rect,
                4
            )

        if pedal2_pressed:

            pygame.draw.rect(
                screen,
                HIGHLIGHT_COLOR,
                pedal2_rect,
                4
            )

        # ----------------------------------------------------
        # PEDAL LABELS
        # ----------------------------------------------------

        screen.blit(
            font.render(
                "Pedal 1",
                True,
                BLACK
            ),
            (
                pedal1_rect.x - 10,
                pedal1_rect.y - 20
            )
        )

        screen.blit(
            font.render(
                "Pedal 2",
                True,
                BLACK
            ),
            (
                pedal2_rect.x - 10,
                pedal2_rect.y - 20
            )
        )

        pygame.draw.rect(
            screen,
            RESET_BUTTON_COLOR,
            reset_rect,
            border_radius=6
        )

        screen.blit(
            font.render("Reset", True, WHITE),
            (reset_rect.x + 30, reset_rect.y + 12)
        )

        pygame.draw.rect(
            screen,
            BLACK,
            (
                warpA_x[0],
                frame1_y,
                frame1_width,
                frame_height
            )
        )

        pygame.draw.rect(
            screen,
            DARK_GREY,
            (
                warpB_x[0],
                frame2_y,
                frame2_width,
                frame_height
            )
        )

        

        screen.blit(
            font.render(
                "Frame 1",
                True,
                BLACK
            ),
            (
                warpA_x[0] + 10,
                frame1_y - 20
            )
        )

        screen.blit(
            font.render(
                "Frame 2",
                True,
                BLACK
            ),
            (
                warpB_x[0] + 80,
                frame2_y - 20
            )
        )

       
        for segment in weft_path:

            pygame.draw.line(
                screen,
                WEFT_COLOR,
                segment[0],
                segment[1],
                4
            )

       

        if weft_path:

            screen.blit(
                font.render(
                    "Weft Shuttle",
                    True,
                    BLACK
                ),
                (
                    shuttle_x - 40,
                    shuttle_y - 15
                )
            )

        

        for col, warp_x in enumerate(all_warp_x):

            if warp_x in warpA_x:

                top_y = (
                    frame1_y
                    + frame_height
                )

            else:

                top_y = (
                    frame2_y
                    + frame_height
                )

            bottom_y = (
                top_y
                + warp_length
            )

            last_y = top_y

            for row in range(cycle_count):

                y = (
                    max(
                        frame1_y_orig,
                        frame2_y_orig
                    )
                    + frame_height
                    + row * weft_drop
                )

                if cloth_state[col][row]:

                    pygame.draw.line(
                        screen,
                        WARP_COLOR,
                        (
                            warp_x,
                            last_y
                        ),
                        (
                            warp_x,
                            min(
                                y - 2,
                                bottom_y
                            )
                        ),
                        3
                    )

                else:

                    pygame.draw.line(
                        screen,
                        WARP_COLOR,
                        (
                            warp_x,
                            last_y
                        ),
                        (
                            warp_x,
                            min(
                                y + 2,
                                bottom_y
                            )
                        ),
                        3
                    )

                last_y = min(
                    y,
                    bottom_y
                )

            pygame.draw.line(
                screen,
                WARP_COLOR,
                (
                    warp_x,
                    last_y
                ),
                (
                    warp_x,
                    bottom_y
                ),
                3
            )

        

        if shuttle_moving:

            pygame.draw.rect(
                screen,
                SHUTTLE_COLOR,
                (
                    shuttle_x - 10,
                    shuttle_y - 5,
                    20,
                    10
                )
            )



        pygame.display.flip()

       

        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())

#
# Author: Kılıçarslan SIMSIKI
#


import pygame
import ctypes


def get_screen_size():
    user32 = ctypes.windll.user32
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)


def main(height, width, barray):
    pygame.init()

    # Get the screen size
    screen_width, screen_height = get_screen_size()

    # Calculate the maximum pixel size that will fit on the screen
    max_pxsize_width = (screen_width - 100) // width  # Leave some margin
    max_pxsize_height = (screen_height - 100) // height  # Leave some margin
    pxsize = min(max_pxsize_width, max_pxsize_height, 20)  # Use the smaller value, but cap at 20

    # Calculate the grid size
    grid_width = width * pxsize
    grid_height = height * pxsize

    # Create a screen that fits the grid
    screen = pygame.display.set_mode((grid_width, grid_height))
    pygame.display.set_caption("Bitmap Bitarray Converter")

    # (red, green, blue)
    c = (0, 150, 255)
    color_ledoff = (0, 0, 0)
    color_ledon = (255, 255, 0)

    # create a 2D list to keep track of the cell colors
    if len(barray) > 0:
        # read the matrix from the 2D array
        cell_colors = [
            [color_ledon if barray[y][x] == 1 else color_ledoff for y in range(height)] for x in range(width)
        ]
    else:
        # create a 2D array
        cell_colors = [[color_ledoff for y in range(height)] for x in range(width)]

    # Variables for panning
    pan_x, pan_y = 0, 0
    panning = False
    last_mouse_pos = (0, 0)

    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                # check if Ctrl+S keys were pressed
                if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    write_grid_to_file(height, width, cell_colors, color_ledon)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # get the mouse position
                    pos = pygame.mouse.get_pos()
                    # determine the column and row of the cell that was clicked
                    col = (pos[0] - pan_x) // pxsize
                    row = (pos[1] - pan_y) // pxsize
                    if 0 <= col < width and 0 <= row < height:
                        # toggle the color of the cell
                        if cell_colors[col][row] == color_ledoff:
                            cell_colors[col][row] = color_ledon
                        else:
                            cell_colors[col][row] = color_ledoff
                elif event.button == 3:  # Right click
                    panning = True
                    last_mouse_pos = event.pos
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3:  # Right click release
                    panning = False
            elif event.type == pygame.MOUSEMOTION:
                if panning:
                    dx = event.pos[0] - last_mouse_pos[0]
                    dy = event.pos[1] - last_mouse_pos[1]
                    pan_x += dx
                    pan_y += dy
                    last_mouse_pos = event.pos

        screen.fill((50, 50, 50))  # Fill with dark gray

        # draw the cells
        for x in range(width):
            for y in range(height):
                color = cell_colors[x][y]
                pygame.draw.rect(
                    screen, color, pygame.Rect(x * pxsize + pan_x, y * pxsize + pan_y, pxsize, pxsize)
                )

                # draw the grid lines
                pygame.draw.line(
                    screen,
                    c,
                    (x * pxsize + pan_x, y * pxsize + pan_y),
                    (x * pxsize + pan_x + pxsize, y * pxsize + pan_y),
                    1,
                )  # horizontal line
                pygame.draw.line(
                    screen,
                    c,
                    (x * pxsize + pan_x, y * pxsize + pan_y),
                    (x * pxsize + pan_x, y * pxsize + pan_y + pxsize),
                    1,
                )  # vertical line

        pygame.display.update()

    pygame.quit()


# function to read from file into a 2D array
def read_grid_from_file():
    barray = []  # will contain lists. e.g [[1,0,1,0], [0,0,0,1]]
    row = []
    with open("grid.cpp", "r") as f:
        for _ in range(3):
            f.readline()
        while True:
            line = f.readline()
            if not line:
                # Reached the end of the file
                break
            if line != "};":
                row = line.strip().split("},")[0].split("{")[1].split(",")
                if row[-1].endswith("}"):
                    # remove the last character '}'
                    row[-1] = row[-1][:-1]
                row = [int(x) for x in row]
                barray.append(row)

    main(len(barray), len(barray[0]), barray)


# function to write the current grid to a file
def write_grid_to_file(height, width, cell_colors, color_ledon):
    bit_string = ""
    with open("grid.cpp", "w") as f:
        f.write(f"// {height}x{width}\n")
        f.write("std::vector<std::vector<int>> PatternAnimator::grid =" + "\n")
        f.write("{" + "\n")
        for y in range(height):
            f.write("\t{")
            for x in range(width):
                if cell_colors[x][y] == color_ledon:
                    bit_string += "1"
                    if x != width - 1:
                        f.write("1,")
                    else:
                        f.write("1")
                else:
                    bit_string += "0"
                    if x != width - 1:
                        f.write("0,")
                    else:
                        f.write("0")
            if y != height - 1:
                f.write("},")
            else:
                f.write("}")
            f.write("\n")
        f.write("};")
        f.write("\n")
        f.write(bit_string)

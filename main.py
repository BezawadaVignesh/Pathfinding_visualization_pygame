from tkinter import Message
import pygame as pg
import pygame_gui as pgui
import pygame.freetype
import math

pg.init()

pg.display.set_caption("Path algo Finding Visualization")


def declare_var():
    global all_pathfinding_alogo, differtent_types, tools_to_draw
    global maze, SW, SH, start_img, end_img, selection_img
    
    all_pathfinding_alogo = ["A*"]
    tools_to_draw = ["Draw walls", "Change startpoint", "Change endpoint"]
    differtent_types = ["Manhattan", "Euclidean"]

    maze= [[0 for i in range(64)] for j in range(27)]
    SW, SH = 1280, 720
    start_img, end_img = pg.image.load('tools/start.png'), pg.image.load('tools/finesh.png')
    start_img, end_img = pg.transform.scale(start_img, (20, 20)), pg.transform.scale(end_img, (20, 20))


class Node:
    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = 0 
        self.h = 0
        self.f = 0
    def __eq__(self, other):
        return self.position == other.position


def heuristic(node, goal, type):
    if type=="Manhattan":
        dx = abs(node.position[0] - goal.position[0])
        dy = abs(node.position[1] - goal.position[1])
        return 2 * (dx + dy)
    elif type=="Euclidean":
        dx = abs(node.position[0] - goal.position[0])
        dy = abs(node.position[1] - goal.position[1])
        return 2 * math.sqrt(dx * dx + dy * dy)


def astar(maze, start, end, winmg, type, msg, cost):
    # Create start and end node
    start_node = Node(None, start)
    start_node.g = start_node.h = start_node.f = 0
    end_node = Node(None, end)
    end_node.g = end_node.h = end_node.f = 0

    # Initialize both open and closed list
    open_list = []
    closed_list = []

    # Add the start node
    open_list.append(start_node)
    on_button = False
    # Loop until you find the end
    while len(open_list) > 0:
        # updating on screen
        winmg.update(maze, msg)
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return None
            if event.type == pg.MOUSEBUTTONDOWN:
                if on_button:
                    return None
            if event.type == pg.USEREVENT:
                if event.user_type == pgui.UI_BUTTON_PRESSED:
                    if event.ui_object_id == "stop_butten":
                        return None
                elif event.user_type == 3:
                    if event.ui_object_id == "stop_butten":
                        on_button=True
                elif event.user_type == 4:
                    if event.ui_object_id == "stop_butten":
                        on_button=False
                
        
        # Get the current node
        current_node = open_list[0]
        current_index = 0
        for index, item in enumerate(open_list):
            if item.f < current_node.f:
                current_node = item
                current_index = index

        # Pop current off open list, add to closed list
        open_list.pop(current_index)
        if maze[current_node.position[0]][current_node.position[1]] >= 0:
            maze[current_node.position[0]][current_node.position[1]] = 2
        closed_list.append(current_node)

        # Found the goal
        if current_node == end_node:
            path = []
            current = current_node
            while current is not None:
                path.append(current.position)
                current = current.parent
                
            return path[::-1] # Return reversed path

        # Generate children
        children = []
        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]: # Adjacent squares

            # Get node position
            node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

            # Make sure within range
            if node_position[0] > (len(maze) - 1) or node_position[0] < 0 or node_position[1] > (len(maze[len(maze)-1]) -1) or node_position[1] < 0:
                continue

            # Make sure walkable terrain
            if maze[node_position[0]][node_position[1]] != 0 and maze[node_position[0]][node_position[1]] != -2:
                continue

            # Create new node
            new_node = Node(current_node, node_position)

            # Append
            children.append(new_node)

        # Loop through children
        for child in children:

            # Child is on the closed list
            for closed_child in closed_list:
                if child == closed_child:
                    continue

            # Create the f, g, and h values
            child.g = current_node.g + cost
            child.h = heuristic(child, end_node, type)
            child.f = child.g + child.h

            # Child is already in the open list
            for open_node in open_list:
                if child == open_node and child.g > open_node.g:
                    continue

            # Add the child to the open list
            open_list.append(child)
            if maze[child.position[0]][child.position[1]] >= 0:
                maze[child.position[0]][child.position[1]] = 3


class WindowManager:
    def __init__(self, sw, sh):
        self.sw = sw
        self.sh = sh
        self.window = pg.display.set_mode((self.sw, self.sh))
        self.ui_manager = pgui.UIManager((self.sw, self.sh))
        self.add_ui_elements()

    def text_to_screen(self, text, color, pos, font_size):
        font_used = pg.freetype.Font("Basic-Regular.ttf", font_size)
            
        font_used.render_to(self.window, pos, text, color)

    def add_ui_elements(self):
        self.start_button = pgui.elements.UIButton(relative_rect=pg.Rect((975, 25), (100, 50)),
                                                text='Start',
                                                manager=self.ui_manager, object_id="start_butten")
        self.reset_button = pgui.elements.UIButton(relative_rect=pg.Rect((1125, 25), (100, 50)),
                                                text='Reset',
                                                manager=self.ui_manager, object_id="reset_butten")
        self.stop_button = pgui.elements.UIButton(relative_rect=pg.Rect((1125, 90), (100, 50)),
                                                text='Stop',
                                                manager=self.ui_manager, object_id="stop_butten")
        self.stop_button.disable()
        self.current_path_algo = pgui.elements.UIDropDownMenu(options_list=all_pathfinding_alogo,
                                                                starting_option="Algorithm",
                                                                relative_rect=pg.Rect(30, 25, 180, 30), manager=self.ui_manager,
                                                                object_id="current_path_algo")
        self.drawing_tool = pgui.elements.UIDropDownMenu(options_list=tools_to_draw,
                                                                starting_option="Tools",
                                                                relative_rect=pg.Rect(430, 25, 180, 30), manager=self.ui_manager,
                                                                object_id="drawing_tool")
        self.different_types = pgui.elements.UIDropDownMenu(options_list=differtent_types,
                                                                starting_option="Manhattan",
                                                                relative_rect=pg.Rect(230, 25, 180, 30), manager=self.ui_manager,
                                                                object_id="different_types")
        self.cost_slider = pgui.elements.UIHorizontalSlider(relative_rect=pg.Rect(75, 85, 200, 22),
                                                                   start_value=1,
                                                                   value_range=(1,20), manager=self.ui_manager,
                                                                   object_id="cost_slider")

    def draw_title(self, msg):
        self.text_to_screen(text="Cost: ", color=(250,250,250), pos=(33, 88), font_size=18)
        self.text_to_screen(text=msg, color=(250,250,250), pos=(10, 150), font_size=20)

    def draw_screen(self, maze):
        W, H = self.sw, 3*(self.sh//4)
        screen = pg.Surface((W, H))
        screen.fill((0, 0, 0))
        self.window.blit(screen, (0, H//3))
        blockSize = 20 # size of the grid block
        i, j = 0,0
        for x in range(0, W, blockSize):
            j=0
            for y in range(180, H+180, blockSize):
                rect = pg.Rect(x, y, blockSize, blockSize)
                if maze[j][i] == 0:         #clear block
                    pg.draw.rect(self.window, (255,255,255), rect)
                elif maze[j][i] == 1:       # Wall
                    pg.draw.rect(self.window, (25,50,200), rect)
                elif maze[j][i] == 2:       # Visited
                    pg.draw.rect(self.window, (173,216,230), rect)
                elif maze[j][i] == 3:       # Yet to visit
                    pg.draw.rect(self.window, (255,255,255), rect)
                    pg.draw.circle(self.window, (75,100,200), (x+10, y+10), 5)
                elif maze[j][i] == 5:       # Final path
                    pg.draw.rect(self.window, (255,255,51), rect)
                elif maze[j][i] == -1:
                    self.window.blit(start_img, (x,y))
                elif maze[j][i] == -2:
                    self.window.blit(end_img, (x,y))
                j+=1
            i+=1
        
        # drawings lines
        for i in range(180, 720, 20):
            pg.draw.line(self.window, (180, 180, 180), (0, i), (W, i))
        for i in range(0, W, 20):
            pg.draw.line(self.window, (180, 180, 180), (i, 180), (i, 720))


    def update(self, maze, msg):
        delta_time = pg.time.Clock().tick(60)/1000.0
        self.window.fill(pg.Color("#322f3d"))
        self.draw_screen(maze)
        self.draw_title(msg)
        self.ui_manager.update(delta_time)
        self.ui_manager.draw_ui(self.window)

        pg.display.update()


def main():
    global maze
    cost = 1
    winmg = WindowManager(SW, SH)
    run = True
    drawing = 0
    status_message = "This program can be used to visualize different pathfinding algorithm but present there is only A* pathfinding"
    # default args
    start, finesh = (0,0), (24,25)
    maze[start[0]][start[1]], maze[finesh[0]][finesh[1]] = -1, -2
    
    algo_to_use = ""
    type = "Manhattan"
    
    while run: 
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
                break
            if event.type == pg.MOUSEBUTTONDOWN:
                if drawing == -1:
                    x,y = pygame.mouse.get_pos()
                    if 180 < y < SH and 0 < x < SW:
                        drawing= 1
                        if maze[((y-180)//20)][(x//20)] >= 0:
                            if maze[((y-180)//20)][(x//20)] == 0:
                                maze[((y-180)//20)][(x//20)] = 1
                            elif maze[((y-180)//20)][(x//20)] == 1:
                                maze[((y-180)//20)][(x//20)] = 0
   
            elif event.type == pg.MOUSEBUTTONUP:
                if drawing == 1:
                    drawing = -1
                elif drawing == 2 or drawing == 3:
                    x,y = pygame.mouse.get_pos()
                    if 180 < y < SH and 0 < x < SW:
                        if drawing == 2:
                            maze[start[0]][start[1]] = 0
                            maze[((y-180)//20)][(x//20)] = -1
                            start = (((y-180)//20), (x//20))
                        elif drawing == 3:
                            maze[finesh[0]][finesh[1]] = 0
                            maze[((y-180)//20)][(x//20)] = -2
                            finesh = (((y-180)//20), (x//20))

            elif drawing==1 and event.type == pg.MOUSEMOTION:
                x,y = pygame.mouse.get_pos()
                if 180 < y < SH and 0 < x < SW:
                    if drawing == 1:
                        maze[((y-180)//20)][(x//20)] = 1
            
            if event.type == pg.USEREVENT:
                if event.user_type == pgui.UI_HORIZONTAL_SLIDER_MOVED:
                    if event.ui_element == winmg.cost_slider:
                        cost = event.value
                if event.user_type == pgui.UI_BUTTON_PRESSED:
                    if event.ui_element == winmg.start_button:
                        status_message = 'Finding path using "'+algo_to_use+' pathfinding algorithm"'
                        for i in range(len(maze)):
                            for j in range(len(maze[0])):
                                if maze[i][j]>1:
                                    maze[i][j]=0
                        if algo_to_use == "A*":
                            winmg.start_button.disable()
                            winmg.reset_button.disable()
                            winmg.stop_button.enable()
                            path = astar(maze=maze, start=start, end=finesh, winmg=winmg, type=type, msg=status_message, cost=cost)
                            
                            winmg.stop_button.disable()
                            winmg.start_button.enable()
                            winmg.reset_button.enable()
                            if not path:
                                status_message="Path finding stoped or no path found!"
                                continue
                            else:
                                status_message="Shortest path is "+str(len(path))+" blocks"
                            for i in path:
                                maze[i[0]][i[1]] = 5
                                maze[start[0]][start[1]], maze[finesh[0]][finesh[1]] = -1, -2
                        else:
                            status_message="Plese select a algorithm first"
                        

                    elif event.ui_element == winmg.reset_button:
                        status_message = "Board has been reset."
                        winmg.start_button.enable()
                        maze= [[0 for _ in range(64)] for __ in range(27)]
                        maze[start[0]][start[1]], maze[finesh[0]][finesh[1]] = -1, -2
                
                elif event.user_type == pgui.UI_DROP_DOWN_MENU_CHANGED:
                    if event.ui_object_id == "current_path_algo":
                        algo_to_use = event.text
                    elif event.ui_object_id == "drawing_tool":
                        to_find = tools_to_draw.index(event.text)
                        if to_find == 0:
                            status_message="Select squares to make them a wall."
                            drawing = -1
                        elif to_find == 1:
                            status_message="Select a box to make it the starting point"
                            drawing = 2
                        elif to_find == 2:
                            status_message="Select a box to make it the ending point"
                            drawing = 3
                    elif event.ui_object_id == "different_types":
                        status_message=event.text+" has been selected"
                        type = event.text
            

            winmg.ui_manager.process_events(event)
        winmg.ui_manager.update(pg.time.Clock().tick(60)/1000.0)
        winmg.update(maze, status_message)
    
    pg.quit()

if __name__=="__main__":
    declare_var()
    main()
    

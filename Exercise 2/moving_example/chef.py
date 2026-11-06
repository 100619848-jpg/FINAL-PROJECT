import random


class Chef:
    """ A first version of the Chef class for the final project. It just
    contains properties and setters. It may or not have a dish """
    def __init__(self, x: int, y: int):
        """ Init method of the class
        :param x: the x of the chef
        :param y: the y of the chef
        """
        self.x = x
        self.y = y
        # The initial sprite will be always the same, so no parameter is needed
        # In Pyxel the image is a tuple with the coordinates of the image in
        # the image bank.
        # The tuple is (image_bank, starting_x, starting_y, horizontal_size,
        # vertical_size)
        # It would be a good idea to make the sprite read-only, we will see how
        # to do it in next lectures
        self.image = (0, 0, 0, 16, 16)
        value = random.randint(0, 1)
        if value == 1:
            self.has_dish = True
        else:
            self.has_dish = False

    @property
    def x(self) -> int:
        return self.__x

    @property
    def y(self) -> int:
        return self.__y

    @property
    def image(self) -> tuple:
        return self.__image

    @property
    def has_dish(self) -> bool:
        return self.__has_dish

    @x.setter
    def x(self, x: int):
        if not isinstance(x, int):
            raise TypeError("The x position must be an int")
        elif x < 0:
            raise ValueError("The x cannot be negative")
        else:
            self.__x = x

    @y.setter
    def y(self, y: int):
        if not isinstance(y, int):
            raise TypeError("The y position must be an int")
        elif y < 0:
            raise ValueError("The y cannot be negative")
        else:
            self.__y = y

    @image.setter
    def image(self, image: tuple):
        if not isinstance(image, tuple):
            raise TypeError("The image must be a tuple with 5 elements")
        elif len(image) != 5:
            raise ValueError("The image must be a tuple with 5 elements")
        else:
            self.__image = image

    @has_dish.setter
    def has_dish(self, dish: bool):
        if not isinstance(dish, bool):
            raise TypeError("The has_dish attribute must be bool")
        else:
            self.__has_dish = dish

    def move(self, direction: str, board_x_size: int, board_y_size: int):
        """
        This is an example of how to move the chef horizontally. No obstacles
        in the board are considered.
        :param direction: a string which can be 'left' or 'right'
        :param board_x_size: the horizontal size of the board, to check the
         limits
        """
        DIRECTIONS = ("left", "right", "up", "down")
        # Checking the type and value of the parameters
        if not isinstance(direction, str):
            raise TypeError("The direction must be a string")
        elif not isinstance(board_x_size, int):
            raise TypeError("The board_x_size must be an integer")
        elif board_x_size < 1:
            raise ValueError("The board_x_size must be a positive integer")
        elif not isinstance(board_y_size, int):
            raise TypeError("The board_y_size must be an integer")
        elif board_y_size < 1:
            raise ValueError("The board_y_size must be a positive integer")
        elif direction.lower() not in DIRECTIONS:
            raise ValueError("The direction must be 'left', 'right', 'up', or 'down'")
        # We convert the direction to lower case to avoid problems with upper
        # case letters
        direction = direction.lower()
        # The (0, 0) position of the chef is the top left corner of the
        # sprite. We can move the chef to the right if the rightmost
        # x-coordinate of the chef is less than the board size. It will be
        # the x-coordinate of the chef plus the width of the sprite. The
        # width of the sprite is the 4th element of the image tuple.
        if direction == "right" and self.x + self.image[3] < board_x_size:
            self.x += 1
        # We can move the chef to the left if its x-coordinate is > 0
        if direction == "left" and self.x > 0:
            self.x -= 1
        # We can move the chef up if its y-coordinate is > 0
        if direction == "up" and self.y > 0:
            self.y -= 1
        # We can move the chef down if its y-coordinate plus the height of the sprite is less than the board size
        if direction == "down" and self.y + self.image[4] < board_y_size:
            self.y += 1

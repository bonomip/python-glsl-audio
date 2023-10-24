
############################## Imports   ######################################
#region
import glfw
import glfw.GLFW as GLFW_CONSTANTS
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import numpy as np
#endregion
############################## Constants ######################################
#region
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
UNIFORM_TYPE = {
    "RESOLUTION": 0,
    "TIME": 1,
}
#endregion
############################## helper functions ###############################
#region
def create_shader(vertex_filepath: str, fragment_filepath: str) -> int:
    """
        Compile and link shader modules to make a shader program.

        Parameters:

            vertex_filepath: path to the text file storing the vertex
                            source code
            
            fragment_filepath: path to the text file storing the
                                fragment source code
        
        Returns:

            A handle to the created shader program
    """

    with open(vertex_filepath,'r') as f:
        vertex_src = f.readlines()

    with open(fragment_filepath,'r') as f:
        fragment_src = f.readlines()
    
    shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                            compileShader(fragment_src, GL_FRAGMENT_SHADER))
    
    return shader
#endregion
###############################################################################
#region
class Square:
    """
        Yep, it's a square.
    """
    __slots__ = ("vao", "vbo", "vertex_count")

    def __init__(self):
        """
            Initialize the square.
        """
        
        # x, y
        vertices = [
        -1.0, 1.0,
        -1.0, -1.0,
        1.0, 1.0,
        1.0, -1.0,  
        ]

        vertices = np.array(vertices, dtype=np.float32)
        self.vertex_count = 4

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

        glEnableVertexAttribArray(0)

        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))

        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        glBindBuffer(GL_ARRAY_BUFFER, 0)

        
    
    def arm_for_drawing(self) -> None:
        """
            Arm the square for drawing.
        """
        glBindVertexArray(self.vao)
    
    def draw(self) -> None:
        """
            Draw the square.
        """

        glDrawArrays(GL_TRIANGLE_STRIP, 0, self.vertex_count)

    def destroy(self) -> None:
        """
            Free any allocated memory.
        """
        
        glDeleteVertexArrays(1,(self.vao,))
        glDeleteBuffers(1,(self.vbo,))

class Shader:
    """
        A shader.
    """
    __slots__ = ("program", "single_uniforms", "multi_uniforms")


    def __init__(self, vertex_filepath: str, fragment_filepath: str):
        """
            Initialize the shader.

            Parameters:

                vertex_filepath: filepath to the vertex source code.

                fragment_filepath: filepath to the fragment source code.
        """

        self.program = create_shader(vertex_filepath, fragment_filepath)

        self.single_uniforms: dict[int, int] = {}
        self.multi_uniforms: dict[int, list[int]] = {}
    
    def cache_single_location(self, 
        uniform_type: int, uniform_name: str) -> None:
        """
            Search and store the location of a uniform location.
            This is for uniforms which have one location per variable.
        """

        self.single_uniforms[uniform_type] = glGetUniformLocation(
            self.program, uniform_name)
    
    def cache_multi_location(self, 
        uniform_type: int, uniform_name: str) -> None:
        """
            Search and store the location of a uniform location.
            This is for uniforms which have multiple locations per variable.
            e.g. Arrays
        """

        if uniform_type not in self.multi_uniforms:
            self.multi_uniforms[uniform_type] = []
        
        self.multi_uniforms[uniform_type].append(
            glGetUniformLocation(
            self.program, uniform_name)
        )
    
    def fetch_single_location(self, uniform_type: int) -> int:
        """
            Returns the location of a uniform location.
            This is for uniforms which have one location per variable.
        """

        return self.single_uniforms[uniform_type]
    
    def fetch_multi_location(self, 
        uniform_type: int, index: int) -> int:
        """
            Returns the location of a uniform location.
            This is for uniforms which have multiple locations per variable.
            e.g. Arrays
        """

        return self.multi_uniforms[uniform_type][index]

    def use(self) -> None:
        """
            Use the program.
        """

        glUseProgram(self.program)
    
    def destroy(self) -> None:
        """
            Free any allocated memory.
        """

        glDeleteProgram(self.program)

class GraphicsEngine:
    """
        Draws entities and stuff.
    """
    __slots__ = ("meshes", "materials", "shaders")


    def __init__(self):
        """
            Initializes the rendering system.
        """

        self._set_up_opengl()

        self._create_assets()

        self._get_uniform_locations()
    
    def _set_up_opengl(self) -> None:
        """
            Configure any desired OpenGL options
        """

        glClearColor(1.0, 1.0, 1.0, 1)
        glEnable(GL_DEPTH_TEST)

    def _create_assets(self) -> None:
        """
            Create all of the assets needed for drawing.
        """

        self.meshes = [
            Square()
        ]

        self.shaders = [ Shader(
            vertex_filepath = "shaders/vertex.txt", 
            fragment_filepath = "shaders/fragment.txt")
        ]

    def _get_uniform_locations(self) -> None:
        """
            Query and store the locations of shader uniforms
        """
        shader = self.shaders[0]
        shader.use()

        shader.cache_single_location(UNIFORM_TYPE["RESOLUTION"], "u_resolution")
        shader.cache_single_location(UNIFORM_TYPE["TIME"], "u_time")

    
    def render(self, time) -> None:
        """
            Draw everything.

        """

        #refresh screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        shader = self.shaders[0]
        shader.use()

        glUniform2f(shader.fetch_single_location(UNIFORM_TYPE["RESOLUTION"]), SCREEN_WIDTH, SCREEN_HEIGHT);
        glUniform1f(shader.fetch_single_location(UNIFORM_TYPE["TIME"]),  time);

        self.meshes[0].arm_for_drawing()
        self.meshes[0].draw()

        glBindVertexArray( 0 )
        glUseProgram( 0 )

        glFlush()

    def destroy(self) -> None:
        """ free any allocated memory """

        for mesh in self.meshes:
            mesh.destroy()
        for shader in self.shaders:
            shader.destroy()

class App:
    """
        The control class.
    """
    __slots__ = (
        "window", "renderer", "scene", "last_time", 
        "current_time", "frames_rendered", "frametime",
        "_keys")

    def __init__(self):
        """ Initialise the program """

        self._set_up_glfw()

        self._set_up_timer()
        
        self._set_up_input_systems()

        self._create_assets()
    
    def resize_cb(self, window, w, h):
        global SCREEN_WIDTH
        global SCREEN_HEIGHT
        SCREEN_WIDTH = w
        SCREEN_HEIGHT = h

    def _set_up_glfw(self) -> None:
        """
            Initialize and configure GLFW
        """

        glfw.init()
        glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MAJOR,3)
        glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MINOR,3)
        glfw.window_hint(
            GLFW_CONSTANTS.GLFW_OPENGL_PROFILE, 
            GLFW_CONSTANTS.GLFW_OPENGL_CORE_PROFILE)
        glfw.window_hint(GLFW_CONSTANTS.GLFW_OPENGL_FORWARD_COMPAT, GLFW_CONSTANTS.GLFW_TRUE)
        #for uncapped framerate
        glfw.window_hint(GLFW_CONSTANTS.GLFW_DOUBLEBUFFER,GL_FALSE) 
        self.window = glfw.create_window(
            SCREEN_WIDTH, SCREEN_HEIGHT, "Folded Reality", None, None)
        glfw.make_context_current(self.window)
        glfw.set_window_size_callback(self.window, self.resize_cb)
    
    def _set_up_timer(self) -> None:
        """
            Initialize the variables used by the framerate
            timer.
        """

        self.last_time = glfw.get_time()
        self.current_time = 0
        self.frames_rendered = 0
        self.frametime = 0.0

    def _set_up_input_systems(self) -> None:
        """
            Configure the mouse and keyboard
        """

        glfw.set_input_mode(
            self.window, 
            GLFW_CONSTANTS.GLFW_CURSOR, 
            GLFW_CONSTANTS.GLFW_CURSOR_HIDDEN
        )

        self._keys = {}
        glfw.set_key_callback(self.window, self._key_callback)

    def _key_callback(self, window, key, scancode, action, mods) -> None:
        """
            Handle a key event.

            Parameters:

                window: the window on which the keypress occurred.

                key: the key which was pressed

                scancode: scancode of the key

                action: action of the key event

                mods: modifiers applied to the event
        """

        state = False
        match action:
            case GLFW_CONSTANTS.GLFW_PRESS:
                state = True
            case GLFW_CONSTANTS.GLFW_RELEASE:
                state = False
            case _:
                return

        self._keys[key] = state

    def _create_assets(self) -> None:
        """
            Create all of the assets needed for drawing.
        """

        self.renderer = GraphicsEngine()

    def run(self) -> None:
        """
            Run the program.
        """

        running = True
        while (running):
            #check events
            if glfw.window_should_close(self.window) \
                or self._keys.get(GLFW_CONSTANTS.GLFW_KEY_ESCAPE, False):
                running = False

            glfw.poll_events()
            
            self.renderer.render(self.current_time)

            #timing
            self._calculate_framerate()

    def _calculate_framerate(self) -> None:
        """
            Calculate the framerate and frametime,
            and update the window title.
        """
        
        self.current_time = glfw.get_time()
        delta = self.current_time - self.last_time
        if (delta >= 1):
            framerate = max(1,int(self.frames_rendered/delta))
            glfw.set_window_title(self.window, f"Running at {framerate} fps.")
            self.last_time = self.current_time
            self.frames_rendered = -1
            self.frametime = float(1000.0 / max(1,framerate))
        self.frames_rendered += 1

    def quit(self):
        
        self.renderer.destroy()
#endregion
###############################################################################
my_app = App()
my_app.run()
my_app.quit()
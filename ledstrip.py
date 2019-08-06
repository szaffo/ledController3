import pigpio
import threading
import time
import math

class Strip(object):

	def __init__(self):
		self.partOfAScene = False

	@property
	def partOfAScene(self):
		return self._partOfAScene

	@partOfAScene.setter
	def partOfAScene(self, value):
		if not isinstance(value, bool):
			raise Exception("Only bool value allowed")

		self._partOfAScene = value
	

class RGBLEDStrip(Strip):

	def __init__(self, red, green, blue):
		super().__init__()

		gp = pigpio.pi()

		gp.set_mode(red, pigpio.OUTPUT)
		gp.set_mode(green, pigpio.OUTPUT)
		gp.set_mode(blue, pigpio.OUTPUT)

		gp.set_PWM_range(red, 255)
		gp.set_PWM_range(green, 255)
		gp.set_PWM_range(blue, 255)

		gp.set_PWM_frequency(red, 100)
		gp.set_PWM_frequency(blue, 100)
		gp.set_PWM_frequency(green, 100)

		self.gp = gp

		self.pin_red = red
		self.pin_green = green
		self.pin_blue = blue

		self.red = 0
		self.green = 255
		self.blue = 0

	@property
	def red(self):
		return self.gp.get_PWM_dutycycle(self.pin_red)

	@property
	def green(self):
		return self.gp.get_PWM_dutycycle(self.pin_green)

	@property
	def blue(self):
		return self.gp.get_PWM_dutycycle(self.pin_blue)

	@red.setter
	def red(self, value):
		self.gp.set_PWM_dutycycle(self.pin_red, value)

	@green.setter
	def green(self, value):
		self.gp.set_PWM_dutycycle(self.pin_green, value)

	@blue.setter
	def blue(self, value):
		self.gp.set_PWM_dutycycle(self.pin_blue, value)

	@property
	def rgb(self):
		return [self.red, self.green, self.blue]

	@rgb.setter
	def rgb(self, rgb):
		r,g,b = rgb

		self.red = r
		self.green = g
		self.blue = b

	def __del__(self):
		self.red = 0
		self.green = 0
		self.blue = 255
		self.master = 100


class Scene(object):

	def __init__(self, strip):
		if not isinstance(strip, Strip):
			raise Exception("Please provide a Strip object")

		if strip.partOfAScene:
			raise Exception("This strip is already part of a scene")

		strip.partOfAScene = True
		self.strip = strip
		self.stopped = False

	def __del__(self):
		self.strip.partOfAScene = False

	def startPlay(self):
		self.thred = threading.Thread(target=self.play, daemon=True)
		self.thred.start()

	def body(self):
		pass

	def condition(self):
		return True

	def play(self):
		self.playing = True

		while(self.condition() and not self.stopped):
			self.body()

		self.playing = False

	def stop(self):
		self.stopped = True

	def continueScene(self):
		self.stopped = False
		self.startPlay()


class FadeToColor(Scene):

	def __init__(self, strip, rgb):
		super().__init__(strip)

		start = strip.rgb
		target = rgb

		distances = zip(start, target)
		distances = tuple(map(lambda x: abs(x[0] - x[1]), distances))
		mx = max(distances[0], max(distances[1], distances[2]))

		self.steps = mx
		self.stepCounter = mx
		self.step_red = (target[0] - start[0]) / self.steps
		self.step_green = (target[1] - start[1]) / self.steps
		self.step_blue = (target[2] - start[2]) / self.steps

		self.red = start[0]
		self.green = start[1]
		self.blue = start[2]


	def body(self):
		self.red += self.step_red
		self.green += self.step_green
		self.blue += self.step_blue

		self.strip.red = math.ceil(self.red)
		self.strip.green = math.ceil(self.green)
		self.strip.blue = math.ceil(self.blue)

		time.sleep(0.5 / self.steps)
		self.stepCounter -= 1
		# print(self.strip.rgb)

	def condition(self):
		return self.stepCounter > 0

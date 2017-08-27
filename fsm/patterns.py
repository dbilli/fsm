
from fsm.machine import FiniteStateMachine
from fsm.machine import CharInput

#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

class BasePatternMachine(object):
	
	def __init__(self, name):
		self.name = name

		self.s_start = '%s.s' % (name)
		self.s_end   = '%s.e' % (name)

	def create_state_machine(self, fsm=None, parent_group=None):
		
		if fsm is None:
			fsm = FiniteStateMachine()

		fsm.set_state(self.s_start, group=self.name, parent_group=parent_group)
		fsm.set_state(self.s_end  , group=self.name, parent_group=parent_group)
		
		return fsm

#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

class SinglePattern(BasePatternMachine):

	def __init__(self, name, input):
		
		super(SinglePattern, self).__init__(name)

		self.input = input

		self.s_matched = '%s.m' % (name)


	def create_state_machine(self, fsm=None, parent_group=None):

		#         input        e
		#    S -----------> M ---> E

		fsm = super(SinglePattern, self).create_state_machine(fsm=fsm, parent_group=parent_group)

		fsm.set_state(self.s_matched, group=self.name, parent_group=parent_group)


		fsm.set_transition(self.s_start  , self.input                , self.s_matched)
		
		fsm.set_e_transition(self.s_matched, self.s_end)
		

		fsm.set_start(self.s_start)
		fsm.set_end  (self.s_end)
		
		return fsm

#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

class SequencePattern(BasePatternMachine):

	def __init__(self, name, patterns):
		super(SequencePattern, self).__init__(name)

		self.patterns = patterns

	def create_state_machine(self, fsm=None, parent_group=None):



		#       e                                   e
		#    S ---> machine1 > machine2 > machine3 ---> E

		fsm = super(SequencePattern, self).create_state_machine(fsm=fsm, parent_group=parent_group)

		fsm.set_start(self.s_start)
		
		for patterns in self.patterns:
			patterns.create_state_machine(fsm=fsm, parent_group=self.name)

		
		prev_state = self.s_start

		for pattern in self.patterns:

			fsm.set_normal(pattern.s_start)
			fsm.set_normal(pattern.s_end)

			fsm.set_e_transition(prev_state, pattern.s_start)
			
			prev_state = pattern.s_end

		fsm.set_e_transition(prev_state, self.s_end)

		fsm.set_end  (self.s_end)
		
		return fsm

#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

class AlternativePattern(BasePatternMachine):

	def __init__(self, name, patterns):
		super(AlternativePattern, self).__init__(name)

		self.patterns = patterns

	def create_state_machine(self, fsm=None, parent_group=None):

		#       e             e
		#    S ---> PATTERN 1 ---> E
		#      ---> PATTERN 2 --->

		fsm = super(AlternativePattern, self).create_state_machine(fsm=fsm, parent_group=parent_group)

		fsm.set_start(self.s_start)
		
		for pattern in self.patterns:
			pattern.create_state_machine(fsm=fsm, parent_group=self.name)

		for pattern in self.patterns:

			fsm.set_normal(pattern.s_start)
			fsm.set_normal(pattern.s_end)
			
			
			fsm.set_e_transition(self.s_start , pattern.s_start)
			fsm.set_e_transition(pattern.s_end, self.s_end)

		fsm.set_end  (self.s_end)
		
		return fsm

#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

class RepetitionPattern(BasePatternMachine):

	def __init__(self, name, pattern):
		super(RepetitionPattern, self).__init__(name)

		self.pattern = pattern

	def create_state_machine(self, fsm=None, parent_group=None):
		
		fsm = super(RepetitionPattern, self).create_state_machine(fsm=fsm, parent_group=parent_group)
		
		fsm.set_start(self.s_start)
		
		self.pattern.create_state_machine(fsm=fsm, parent_group=self.name)


		fsm.set_normal(self.pattern.s_start)
		fsm.set_normal(self.pattern.s_end)

		#              e
		#          +-------+
		#          |       |
		#       e  V       |  e
		#    S ---> PATTERN ----> E
		

		fsm.set_e_transition(self.s_start      , self.pattern.s_start)

		fsm.set_e_transition(self.pattern.s_end, self.pattern.s_start)

		fsm.set_e_transition(self.pattern.s_end, self.s_end)

		fsm.set_end  (self.s_end)

		return fsm

#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

class OptionalPattern(BasePatternMachine):

	def __init__(self, name, pattern):
		super(OptionalPattern, self).__init__(name)

		self.pattern = pattern

	def create_state_machine(self, fsm=None, parent_group=None):

		fsm = super(OptionalPattern, self).create_state_machine(fsm=fsm, parent_group=parent_group)

		self.pattern.create_state_machine(fsm=fsm, parent_group=self.name)

		fsm.set_start(self.s_start)

		fsm.set_normal(self.pattern.s_start)
		fsm.set_normal(self.pattern.s_end)

		#              e
		#    +--------------------+
		#    |  e             e   v
		#    S ---> PATTERN ----> E
		
		fsm.set_e_transition(self.s_start      , self.pattern.s_start)
		fsm.set_e_transition(self.s_start      , self.s_end)
		fsm.set_e_transition(self.pattern.s_end, self.s_end)

		fsm.set_end  (self.s_end)

		return fsm

#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

if __name__ == "__main__":


	p = SinglePattern('A', CharInput('a'))
	
	p2 = SinglePattern('B', CharInput('b'))

	p = AlternativePattern('OR', [p, p2] )
	
	#p = SequencePattern('AB', [p, p2] )
	
	#p = RepetitionPattern('2', SinglePattern('1','a') )
	
	#p = OptionalPattern('1', 
	#
	#	#SinglePattern('5','a'), 
	#	
	#	#RepetitionPattern('2',
	#	#	SequencePattern('4', [
	#	#		SinglePattern('5','a'), 
	#	#		SinglePattern('6','b'),
	#	#	]),
	#	#),
	#
	#	RepetitionPattern('2',
	#		SequencePattern('3', [
	#			SinglePattern('5','a'), 
	#			SinglePattern('4','b'),
	#		]),
	#	),
	#)

	p = OptionalPattern('1', p)
	
	p = RepetitionPattern('2', p)

	

	
	fsm = p.create_state_machine()
	
	#fsm = fsm.reduce()

	#print "=" * 80
	#
	from fsm.draw import GraphvizDrawer
	d = GraphvizDrawer()
	#
	d.draw(fsm, 'fsm.jpg')
	#
	fsm2 = fsm.reduce()
	d.draw(fsm2, 'fsm2.jpg')


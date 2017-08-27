import time


#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

class MachineInput(object):

	__id = 0

	@staticmethod
	def get_next_id():
		v = MachineInput.__id
		MachineInput.__id += 1
		return v

	def __init__(self, id=None):
		self.id = id or MachineInput.get_next_id()

	def match(self, input):
		raise Exception("NOT IMPLEMENTED")

	def to_string(self):
		return "<%s>" % (self.id)

#----------------------------------------------------------------------#

class Epsilon(MachineInput):
	
	e = u'\u03B5'
	
	def __init__(self):
		super(Epsilon, self).__init__()

	def to_string(self):
		return "%s" % (Epsilon.e)



class CharInput(MachineInput):
	
	def __init__(self, c):
		super(CharInput, self).__init__()
		self.c = c

	def match(self, c):
		return self.c == c
		
	def to_string(self):
		return "{%s}" % (self.c)


#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

class FiniteStateMachine(object): 

	START   = 'START'
	END     = 'END'

	STATE_START  = 'start'
	STATE_NORMAL = 'normal'
	STATE_FINAL  = 'final'

	EPSILON = Epsilon()

	def __init__(self):

		self.inputs = {}

		self.states = {}
		
		self.state_handlers = {}

		#
		# transition_table = {
		# 	<state> : {
		# 		<input>: { 'next_state': <state> }
		# 	
		# 	}
		# }
		#

		self.transition_table = {}
		
		
	def get_initial_state(self):
		start = None
		
		for state, state_info in self.states.items():
			 if (state_info['type'] == FiniteStateMachine.STATE_START):
				start = state
				break
		
		if not start:
			raise Exceptio('NO START')
			
		return self.e_reduce(start)

	def e_reduce(self, state, states=None):
		
			fsm = self
		
			if states is None:
				states = set()
			
			transitions = fsm.transition_table.get(state,{})
			
			for input_id, transitions_info in transitions.items():
				
				
				input = fsm.inputs[input_id]

				#print input_id, input, transitions_info

				for tran in transitions_info:
					next_state = tran['next_state']
					
					#print "\t", next_state
					
					if next_state in states:
						continue

					if input == FiniteStateMachine.EPSILON:
						states.add(next_state)
						states = states | self.e_reduce(next_state, states)
					#else:
					#	states.add(next_state)
					
			return states
					
					
		
	

	def set_state(self, state, **options):
		s = self.states.get(state, self.states.setdefault(state, {'name': state, 'type': FiniteStateMachine.STATE_NORMAL, 'group':None}) )
		s.update( options )
		
	def set_state_handler(self, state, handler):
		self.state_handlers[state] = handler


	def set_normal(self, state):
		self.set_state(state, type=FiniteStateMachine.STATE_NORMAL)

	def set_start(self, state):
		self.set_state(state, type=FiniteStateMachine.STATE_START)

	def set_end(self, state):
		self.set_state(state, type=FiniteStateMachine.STATE_FINAL)


	def set_e_transition(self, start_state, next_state):
		
		self.set_transition(start_state, FiniteStateMachine.EPSILON, next_state)

	def set_transition(self, start_state, input, next_state):
		
		self.inputs[input.id] = input

		self.set_state( start_state )
		self.set_state( next_state  )

		transition_action = {
			'next_state': next_state
		}

		state_transitions = self.transition_table.get(start_state, self.transition_table.setdefault(start_state, {}))

		transitions = state_transitions.get(input.id, state_transitions.setdefault(input.id, []))

		transitions.append( transition_action )

	def reduce(self):
		
		print "REDUCING"
		
		fsm = self
		
		fsm2 = FiniteStateMachine()
		
		s_start = fsm.get_initial_state()
		
		type=FiniteStateMachine.STATE_START
		aggregated = []
		for s in s_start:
			aggregated.append(s)
			for next_s in fsm.e_reduce(s):
				aggregated.append(next_s)
			
			if fsm.states[s]['type'] == FiniteStateMachine.STATE_FINAL:
				type=FiniteStateMachine.STATE_FINAL

		aggregated = sorted(set(aggregated))
		aggregated_state = ';'.join(sorted(aggregated))
		fsm2.set_state(aggregated_state, type=type)
		
		print "START", aggregated_state


		aggregated_to_process = []
		aggregated_to_process.append(aggregated)

		
		turn = 0
		while aggregated_to_process:
			
			print "TURN", turn
			
			start_aggregated = aggregated_to_process.pop()

			start_aggregated_id = ';'.join(sorted(start_aggregated))

			next_aggregated = []
			inputs = []
			
			for s in start_aggregated:
				
				print "\t", s
				
				transitions = fsm.transition_table.get(s,{})
				
				for input_id, transitions_info in transitions.items():

					
					input = fsm.inputs[input_id]
					
					if input.id is FiniteStateMachine.EPSILON.id:
						continue
					
					inputs.append(input)
			
					for tran in transitions_info:
						next_state = tran['next_state']
			
						print "\t" * 2, "TRANSITION", input_id, s_start

						aggregated = []
						aggregated.append(next_state)
						for reduced_s in fsm.e_reduce(next_state):
							aggregated.append(reduced_s)
								
						next_aggregated += aggregated


			next_aggregated = sorted(list(set(next_aggregated)))
			
			if not next_aggregated:
				continue

			print "\t" * 2, next_aggregated

			aggregated_state_id = ';'.join(next_aggregated)

						
			if aggregated_state_id not in fsm2.states:
				
				options = {}
				for s in next_aggregated:
					if fsm.states[s]['type'] in [FiniteStateMachine.STATE_FINAL]:
						options['type'] = FiniteStateMachine.STATE_FINAL

				fsm2.set_state(aggregated_state_id, **options)
					
				aggregated_to_process.append(next_aggregated)
					
				print "\t" * 3, "ADDED"
					
					
			for input in inputs:
					
				print "\t" * 3, "ADDED TRANSITION", input.id, aggregated_state_id
				fsm2.set_transition(start_aggregated_id, input, aggregated_state_id)
			
			turn += 1

			#time.sleep(0.5)

		print fsm2.inputs
		print fsm2.states
		print fsm2.transition_table
		
		
		return fsm2


#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

class MachineRunner(object):
	
	def __init__(self):
		self.machine_state = {
			'current_state': set()
		}
		
	def set_current_state(self, *state):
		self.machine_state['current_state'] = set(*state)
		
	def get_current_state(self):
		return self.machine_state['current_state']
	
	def run_machine(self, fsm, input_data):
		
		current_state = self.get_current_state()
		
		if not current_state:
			current_state = fsm.get_initial_state()
			
			self.set_current_state(current_state)
		
		print "INITIAL STATE", current_state
		
		final_states = set()
		
		for s in current_state:
			
			transitions = fsm.transition_table.get(s,[])
			
			for input_id, state_transitions in transitions.items():
				
				input = fsm.inputs[input_id]
				
				if input == FiniteStateMachine.EPSILON:
					
					continue
				
				if not input.match(input_data):
					continue
				
				for tran in state_transitions:
					next_state = tran['next_state']
				
					print "NEXT_STATE", next_state
					
					handler = fsm.state_handlers.get(next_state, None)
					if handler:
						handler(fsm, s)

					final_states |= fsm.e_reduce(next_state)

		self.set_current_state(final_states)
		
		for s in final_states:
			handler = fsm.state_handlers.get(s, None)
			if handler:
				handler(fsm, s)


if __name__ == "__main__":
	
	fsm = FiniteStateMachine()

	fsm.set_state(FiniteStateMachine.START, type=FiniteStateMachine.STATE_START)
	fsm.set_state(FiniteStateMachine.END  , type=FiniteStateMachine.STATE_FINAL)
	
	fsm.set_state('a_s', group='A')
	fsm.set_state('a_e', group='A')
	
	
	def _print_state(fsm, current_state):
		print "HANDLER", current_state
	
	fsm.set_state_handler('a_e', _print_state)
	
	fsm.set_transition('a_s', CharInput('a'), 'a_e')

	fsm.set_e_transition(FiniteStateMachine.START, 'a_s')

	fsm.set_e_transition('a_e', FiniteStateMachine.END)

	print "-------"
	mr = MachineRunner()
	
	mr.run_machine(fsm, 'a')
	
	print "-------"
	cs = mr.get_current_state()
	print cs

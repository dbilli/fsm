

GROUP_NAME = "g_%s"

GROUP_NAME = "cluster_%s"

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

	def e_reduce(self, state):
		
			states = set()
			
			transitions = fsm.transition_table.get(state,{})
			
			for input_id, transitions_info in transitions.items():
				
				
				input = fsm.inputs[input_id]

				print input_id, input, transitions_info

				for tran in transitions_info:
					next_state = tran['next_state']
					
					print "\t", next_state

					if input == FiniteStateMachine.EPSILON:
						states.add(next_state)
						states = states | self.e_reduce(next_state)
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

	def draw(self, file_name):

		import pygraphviz as pgv

		G = pgv.AGraph(
			name='fsm', 
			rankdir='LR', 
			#rank='same',
			directed=True, 
			# size="24,1000",
			#packmode='node',
			#clusterrank='local', 
			#compound=True, 
			#rank='same ' + ' '.join(self.states.keys()),
			#newrank=True,
			#splines='line',
			#ranksep='10'
		)

		for state, state_info in self.states.items():
			options = {}
			if state_info['type'] in [ FiniteStateMachine.STATE_START, FiniteStateMachine.STATE_FINAL]:
				options['shape'] = "doublecircle"
			G.add_node(state, **options)

		"""
		print G

		states_by_group = {}
		for s in self.states.values():

			g_name = s['group']
			if not g_name:
				continue

			g = states_by_group.get(g_name, states_by_group.setdefault(g_name,set()) )
			g.add(s['name'])



		print 1
		
		groups_by_parent = {}
		for s in self.states.values():

			group_name   = s['group']
			parent_group = s['parent_group']
			
			print group_name, parent_group

			groups_by_parent.get(group_name, groups_by_parent.setdefault(group_name, set()) )
			
			states = groups_by_parent.get(parent_group, groups_by_parent.setdefault(parent_group, set()) )
			states.add(group_name)

		print "----"

		def _create_subgraphs(G, parent_graph=None, parent_group=None, level=0):

			if parent_graph is None:
				print ' ' * level, 'x'
				parent_graph = G

			group_names = groups_by_parent.get(parent_group, [])
			for g_name in group_names:

				states    = list(states_by_group[g_name])
				subgroups = list([GROUP_NAME % (name) for name in groups_by_parent.get(g_name,[])])

				graph = parent_graph.get_subgraph(name=GROUP_NAME % (g_name))
				if graph is None:
					graph = parent_graph.add_subgraph(
						[], 
						name=GROUP_NAME % (g_name), 
						label=g_name, 
						rankdir='LR', 
						clusterrank='local', 
						rank='same ' + ' '.join([ '%s;'%(s) for s in states+subgroups])
					)
					created = True
				else:
					created = False



				print ' ' * level, g_name, states+subgroups, parent_group, repr(parent_graph), created

				for state_name in states:
					
					state_info = self.states[state_name]
					
					options = {
						'rank': 'same'
					}
					if state_info['type'] == FiniteStateMachine.STATE_FINAL:
						options['shape']="doublecircle"
					graph.add_node(state_name, **options)



				_create_subgraphs(G, parent_graph=graph, parent_group=g_name, level=level+1)


		_create_subgraphs(G)
		
		#print G
		
		#for g_name, states in states_by_group.items():
		#	G.add_subgraph(states, name="cluster_%s" % (g_name), label=g_name, rankdir='LR')
		"""
	
		for start_state, transitions in self.transition_table.items():

			for input, state_transition in transitions.items():
				
				input = self.inputs[input]
				
				for transition_info in state_transition:

					next_state = transition_info['next_state']

					state_info = self.states[next_state]


					options = {}
					#if start_state > next_state:
					#	options['weight'] = 0

					G.add_edge(start_state, next_state, label=input.to_string(), **options)

		print G

		G.draw(file_name, prog='dot')

		
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

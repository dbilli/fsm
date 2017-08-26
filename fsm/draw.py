
#import pygraphviz as pgv
import pydot as pgv

from fsm.machine import FiniteStateMachine

class GraphvizDrawer(object):
	
	@staticmethod
	def draw(fsm, file_name):

		

		#G = pgv.AGraph(
		#	name='fsm', 
		#	rankdir='LR', 
		#	#rank='same',
		#	directed=True, 
		#	# size="24,1000",
		#	#packmode='node',
		#	#clusterrank='local', 
		#	#compound=True, 
		#	#rank='same ' + ' '.join(self.states.keys()),
		#	#newrank=True,
		#	#splines='line',
		#	#ranksep='10'
		#)
		
		G = pgv.Dot(graph_type='digraph')
		

		for state, state_info in fsm.states.items():
			options = {}
			if state_info['type'] in [ FiniteStateMachine.STATE_START, FiniteStateMachine.STATE_FINAL]:
				options['shape'] = "doublecircle"
			G.add_node(pgv.Node(state, **options))

		"""
		print G

		states_by_group = {}
		for s in fsm.states.values():

			g_name = s['group']
			if not g_name:
				continue

			g = states_by_group.get(g_name, states_by_group.setdefault(g_name,set()) )
			g.add(s['name'])



		print 1
		
		groups_by_parent = {}
		for s in fsm.states.values():

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
					
					state_info = fsm.states[state_name]
					
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
	
		for start_state, transitions in fsm.transition_table.items():

			for input, state_transition in transitions.items():
				
				input = fsm.inputs[input]
				
				for transition_info in state_transition:

					next_state = transition_info['next_state']

					state_info = fsm.states[next_state]


					label = input.to_string()

					print start_state, label, next_state

					import time
					options = {
						'key'  : label.replace('{','').replace('}',''), 
						'label': label,
					}
					#if start_state > next_state:
					#	options['weight'] = 0
					G.add_edge(pgv.Edge(start_state, next_state, **options))

		print G

		G.write_png(file_name)#, prog='dot')


if __name__ == "__main__":
	
	#G=pgv.AGraph()
	G=pgv.Dot(graph_type='digraph')
	G.add_edge(pgv.Edge('a','b', key='label1', label='label a'))
	G.add_edge(pgv.Edge('a','b', key='label2', label='label b'))
	#for e in G.edges(): print e, e.attr['label']
	G.write_png('fsm.png')

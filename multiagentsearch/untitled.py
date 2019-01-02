   #****************

    def getAction(self, gamestate)
        next_value, next_action = self.minimax_value(gameState, self.index, 0)
        return next_value

    def minimax_value(self, state, agent, depth):
        num_agents = state.getNumAgents()

        #fully explored, score
        if depth == self.depth and agent % num_agents == 0:
            return self.evaluationFunction(state), None

        #its pacman, or a maximizer
        if agent % num_agents == 0:
            return self.maximize_value(state, agent % num_agents, depth)

        #its a ghost, a minimizer
        return self.minimize_value(state, agent % num_agents, depth)

    def minimize_value(self, state, agent, depth):
        successor_states = [(state.generateSuccessor(agent, action), action) for action in state.getLegalActions(agent)]

        if len(successor_states) == 0:
            return self.evaluationFunction(state), None

        value = float("inf")
        value_action = None

        next_agent = agent + 1
        for successor_state, action in successor_states:
            next_value, next_action = self.minimax_value(successor_state, next_agent, depth)
            if next_value < value:
                value = next_value
                value_action = action

        return value, value_action

    def maximize_value(self, state, agent, depth):
        successor_states = [(state.generateSuccessor(agent, action), action) for action in state.getLegalActions(agent)]

        if len(successor_states) == 0:
            return self.evaluationFunction(state), None

        value = -float("inf")
        value_action = None

        next_agent = agent + 1
        next_depth = depth + 1
        for successor_state, action in successor_states:
            next_value, next_action = self.minimax_value(successor_state, next_agent, next_depth)
            if next_value > value:
                value = next_value
                value_action = action

        return value, value_action


        #****************************
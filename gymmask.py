import numpy as np
import random
import matplotlib.pyplot as plt

transmit_rate = 0.001 # Sick masked transmitter to masked target
asymp_rate = transmit_rate/3
mask_percentage = 1

incub_duration = 5
immune_duration = 40
healthy_count = 300
sick_count = 10
timeend_set = 50

spread_probablities = {
  "SMM": transmit_rate,
  "SMN": transmit_rate*1.2, # Sick masked -> Non masked
  "SNM": transmit_rate*1.5,
  "SNN": transmit_rate*2.5,
  "AMM": asymp_rate,
  "AMN": asymp_rate*1.2,
  "ANM": asymp_rate*1.5,
  "ANN": asymp_rate*2.5
}

def char2str(s):
    new = ""
    for x in s:
        new += x
    return new

class population:
    def __init__(self):
        self.agents = [] # array of agents in population
        self.num_agents = 0
        self.num_sick = 0
        self.num_mask = 0

        self.num_immune = 0
        

    def add_agent(self, health_state, mask_state):
        this_agent = agent()
        this_agent.mask_state = mask_state
        this_agent.health_state = health_state
        this_agent.ppl_index =  self.num_agents # ID
        self.agents.append(this_agent)
        
        self.num_agents += 1
        if (mask_state == 'M'): 
            self.num_mask += 1
        if (health_state == 'S'):
            this_agent.sick.flag = True
            self.num_sick += 1
        elif (health_state == 'A'):
            this_agent.asymp.flag = True
            

    def pop_agent(self):
        if self.num_agents > 0:
            del self.agents[-1]
        else:
            print("Population zero")

    def remove_agent(self, index):
        del self.agents[index]

    def print_num_agents(self):
        print(self.num_agents)

class room:
    def __init__(self):
        self.agents = [] # array of agents in room
        self.num_agents = 0
        self.num_sick = 0
        self.num_mask = 0

        self.num_immune = 0

    def complete_fill_room(self, population):
        for i in population.agents:
            i.present = True
            if (i.mask_state == 'M'): 
                self.num_mask += 1
            if (i.health_state == 'S'):
                self.num_sick += 1
            self.num_agents += 1
        for i in population.agents:
            i.assess_room(self)
            self.agents.append(i)
    
    def update_room_stats(self):
        self.num_mask = 0
        self.num_sick = 0
        self.num_immune = 0
        for i in self.agents:
            i.assess_room(self)
            if (i.immune.flag):
                self.num_immune += 1
            if (i.mask_state == 'M'): 
                self.num_mask += 1
            if (i.health_state == 'S'):
                self.num_sick += 1
    
    def enter_agent(self, agent):
        agent.assess_room(self)    
        agent.present = True
        self.agents.append(agent)
        self.num_agents += 1
        if (agent.mask_state == 'M'): 
            self.num_mask += 1
        if (agent.health_state == 'S'):
            self.num_sick += 1
    
    def pop_agent(self):
        if self.num_agents > 0:
            self.agents[-1].present = False
            if (self.agents[-1].mask_state == 'M'): 
                self.num_mask -= 1
            if (self.agents[-1].health_state == 'S'):
                self.num_sick -= 1
            del self.agents[-1]
        else:
            print("Room zero")

    def remove_agent(self, index):
        try:
            self.agents[index].present = False
            if (self.agents[index].mask_state == 'M'): 
                self.num_mask -= 1
            if (self.agents[index].health_state == 'S'):
                self.num_sick -= 1
            del self.agents[index]
        except:
            print("Agent index does not exist")


class health_struct:
    def __init__(self):
        self.flag = False
        self.timer = 0
        self.max = 0

class agent:
    def __init__(self):
        ## A: Agent variables
        self.incub  = health_struct()
        self.asymp  = health_struct()
        self.sick   = health_struct()
        self.immune = health_struct()

        #self.incub.max  = 10
        self.incub.max  = incub_duration
        self.asymp.max  = 2
        self.sick.max   = 2
        #self.immune.max = 10
        self.immune.max = immune_duration

        self.mask_state = 'M'
        self.health_state = 'H'
        self.present = False
        self.ppl_index = 0   
        
        self.mask_cost = np.random.normal(0.1, 0.05)

        self.num_agents = 0
        self.num_sick = 0
        self.num_mask = 0

    def covid_risk(self, mask_state):
        p_s = self.num_sick / self.num_agents
        p_m = self.num_mask / self.num_agents
        if mask_state == "N":
            return p_s + (p_m-0/5)**2
        else:
            return 0.5 * p_s + self.mask_cost + (p_m-0/5)**4

    def assess_room(self, room):
        self.num_agents = room.num_agents
        self.num_mask = room.num_mask
        self.num_sick = room.num_sick

        # Mask wearing decision
        if self.covid_risk("M") > self.covid_risk("N"):
            self.mask_state = "N"
        else:
            self.mask_state = "M"

class game:     
    def __init__(self):
        self.population = population()
        self.room = room()
        self.timestamp = 0
        self.time_end = timeend_set

        self.new_infections_count = 0
        self.current_infected_count = 0

        self.time_array = []
        self.people_present = []
        self.new_infections = []
        self.current_infected = []
        self.current_masks = []
        self.current_sick = []
        self.current_immune = []
        self.current_susceptible = []

        self.avg_kernel = 30
        self.local_avg = []

    
    def add_population(self, ppl_count, health_state, mask_percentage):
        assert health_state == 'H' or health_state == 'S' or health_state == 'A'
        assert mask_percentage <=1 and mask_percentage >= 0

        for i in range(ppl_count):
            mask_rand = random.random()
            mask_state = "N"
            if (mask_rand < mask_percentage):
                mask_state = "M"
            self.population.add_agent(health_state, mask_state)

    def fill_room(self, room_count):
        for i in range(room_count):
            self.room.enter_agent(self.population.agents[i])

    def transmission_calc(self, A, B):
        trans_prob = 0
        ahs = A.health_state
        ams = A.mask_state
        bms = B.mask_state
        s2 = ""
        s = [ahs, ams, bms]
        s2 = char2str(s)
        trans_prob = spread_probablities[s2]
        
        return trans_prob

    def transmission_process(self, transmitter, target):
        infection_roll = random.random()
        if (infection_roll < self.transmission_calc(transmitter, target)):
            target.health_state = 'A'
            target.incub.flag = True
            return True
        else:
            return False

    def run_mask_action(self): # incomplete
        agent_set = self.room.agents
        # assumption that sick person will wear a mask
        for i in agent_set:
            if (i.health_state == 'S'):
                i.mask_state = 'M'
            

    def run_disease(self):
        agent_set = self.room.agents
        self.new_infections_count = 0
        self.current_infected_count = 0
        for i in agent_set:
            if (i.health_state != 'H'):
                 #print(i.health_state)
                 self.current_infected_count += 1
                 for j in agent_set:
                     if (j.health_state == 'H' and (j.immune.flag == False)):
                        if (self.transmission_process(i,j)):
                            self.new_infections_count += 1

        self.room.agents = agent_set

    def increment_timers(self):
        for i in self.room.agents:
            if (i.incub.flag == True):
                i.incub.timer += 1
            elif (i.asymp.flag == True):
                i.asymp.timer += 1
            elif (i.sick.flag == True):
                i.sick.timer += 1
            elif (i.immune.flag == True):
                i.immune.timer += 1
            else:
                pass

            if (i.incub.timer >= i.incub.max):
                i.incub.flag = False
                i.incub.timer = 0
                i.asymp.flag = True
                i.health_state = 'A'
            elif (i.asymp.timer >= i.asymp.max):
                i.asymp.flag = False
                i.asymp.timer = 0
                i.sick.flag = True
                i.health_state = 'S'
            elif (i.sick.timer >= i.sick.max):
                i.sick.flag = False
                i.sick.timer = 0
                i.health_state = 'H'
                i.immune.flag = True
            elif (i.immune.timer >= i.immune.max):
                i.immune.flag = False
                i.immune.timer = 0
            else:
                pass
        
            # Assert that no agents have more than one state
            state_sum = int(i.incub.flag + i.asymp.flag + i.sick.flag + i.immune.flag)
            #print(i.incub.flag, i.asymp.flag, i.sick.flag, i.immune.flag)
            assert(state_sum <= 1) # you need to write the immune logic (ofc)

    def nextstep_game(self):
        self.timestamp += 1
        agent_set = self.room.agents

        self.room.agents = agent_set
        self.run_disease()
        self.increment_timers()

    def run_game(self):
        for i in range(self.time_end):
            self.nextstep_game()
            self.room.update_room_stats()
            self.gen_plot()
        self.show_plot()
        

    def gen_plot(self):
        self.time_array.append(self.timestamp)
        self.people_present.append(len(self.room.agents))
        self.new_infections.append(self.new_infections_count)
        self.current_infected.append(self.current_infected_count)
        self.current_masks.append(self.room.num_mask)
        self.current_sick.append(self.room.num_sick)
        self.current_immune.append(self.room.num_immune)
        self.current_susceptible.append(self.room.num_agents - self.room.num_immune)

        if (self.timestamp < self.avg_kernel):
            self.local_avg.append(sum(self.current_infected)/self.timestamp)
        else:
            self.local_avg.append(sum(self.current_infected[-self.avg_kernel:])/self.avg_kernel)

        #self.current_masks.append()

    def show_plot(self):
        # create data
        x  = self.time_array
        y1 = self.people_present
        y2 = self.new_infections
        y3 = self.current_infected
        y4 = self.local_avg

        y5 = self.current_masks
        y6 = self.current_sick
        y7 = self.current_immune
        y8 = self.current_susceptible

        
        # plot lines
        plt.plot(x, y1, label = "people_present", color = "tab:blue")
        #plt.plot(x, y2, label = "new_infections")
        plt.plot(x, y3, label = "current_infected", color = "tab:orange")
        #plt.plot(x, y4, label = "local_avg curr inf", color = "black")
        #plt.plot(x, y5, label = "current_masks")
        plt.plot(x, y6, label = "current_sick", color = "tab:red")
        plt.plot(x, y7, label = "current_recovered", color = "tab:purple")
        plt.plot(x, y8, label = "current_susceptible", color = "tab:cyan")
        plt.legend(loc='upper right')
        plt.xlabel('Time units')
        plt.ylabel('Agents')
        plt.legend()
        plt.show()
        #self.current_masks.append()


def main():
    mg = game()
    mg.add_population(healthy_count, "H", mask_percentage)
    mg.add_population(sick_count, "S", mask_percentage)
    mg.room.complete_fill_room(mg.population)
    mg.run_game()


if __name__ == "__main__":
    main()

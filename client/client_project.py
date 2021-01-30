import client
import ast
import random
import socket
import time


HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 50001      # The port used by the server
class Agent():
    def __init__(self):
        self.c = client.Client(HOST, PORT)
        self.res = self.c.connect()
        random.seed()  # To become true random, a different seed is used! (clock time)
        self.maxCoord = ast.literal_eval(self.c.execute("info", "maxcoord"))
        self.qLearningTable = {}

    def getConnection(self):
        return self.res

    def getSelfPosition(self):
        return ast.literal_eval(self.c.execute("info", "position"))

    def getGoalPosition(self):
        return ast.literal_eval(self.c.execute("info", "goal"))
    
    def getRewards(self):
        return ast.literal_eval(self.c.execute("info", "rewards"))

    def get_q_table(self):
        return self.qLearningTable

    def getObstacles(self):
        msg = self.c.execute("info","obstacles")
        obst =ast.literal_eval(msg)
        # test
        #print('Received map of obstacles:', obst)
        return obst
    
    def markArrow(self, direction, x, y):
        if direction == 0:
            self.c.execute("marrow", "north" + "," + str(y) + "," + str(x))
        elif direction == 1:
            self.c.execute("marrow", "south" + "," + str(y) + "," + str(x))
        elif direction == 2:
            self.c.execute("marrow", "east" + "," + str(y) + "," + str(x))
        else:
            self.c.execute("marrow", "west" + "," + str(y) + "," + str(x))


    def updateQLearningTable(self, path):
        self.rewards = self.getRewards()
        for i in range(len(path) -1, -1,-1):
            if self.rewards[path[i][0]][path[i][1]] == 0:
                if path[i][1] == (path[i+1][1] +1) :
                    self.qLearningTable[(path[i][0], path[i][1])][0] = (0.9 * self.rewards[path[i+1][0]][path[i+1][1]])
                    self.rewards[path[i][0]][path[i][1]] = (0.9 * self.rewards[path[i+1][0]][path[i+1][1]])
                elif path[i][1] == (path[i+1][1] -1) :
                    self.qLearningTable[(path[i][0], path[i][1])][1] = (0.9 * self.rewards[path[i+1][0]][path[i+1][1]])
                    self.rewards[path[i][0]][path[i][1]] = (0.9 * self.rewards[path[i+1][0]][path[i+1][1]])
                elif path[i][0] == (path[i+1][0] -1) :
                    self.qLearningTable[(path[i][0], path[i][1])][2] = (0.9 * self.rewards[path[i+1][0]][path[i+1][1]])
                    self.rewards[path[i][0]][path[i][1]] = (0.9 * self.rewards[path[i+1][0]][path[i+1][1]])
                elif path[i][0] == (path[i+1][0] +1) :
                    self.qLearningTable[(path[i][0], path[i][1])][3] = (0.9 * self.rewards[path[i+1][0]][path[i+1][1]])
                    self.rewards[path[i][0]][path[i][1]] = (0.9 * self.rewards[path[i+1][0]][path[i+1][1]])
            elif self.rewards[path[i][0]][path[i][1]] > 0 and self.rewards[path[i][0]][path[i][1]] != 100 :
               if (0.9 * self.rewards[path[i+1][0]][path[i+1][1]]) > self.rewards[path[i][0]][path[i][1]]:
                    if path[i][1] == (path[i+1][1] +1) :
                        self.qLearningTable[(path[i][0], path[i][1])][0] = (0.9 * self.rewards[path[i+1][0]][path[i+1][1]])
                        self.rewards[path[i][0]][path[i][1]] = (0.9 * self.rewards[path[i+1][0]][path[i+1][1]])
                    elif path[i][1] == (path[i+1][1] -1) :
                        self.qLearningTable[(path[i][0], path[i][1])][1] = (0.9 * self.rewards[path[i+1][0]][path[i+1][1]])
                        self.rewards[path[i][0]][path[i][1]] = (0.9 * self.rewards[path[i+1][0]][path[i+1][1]])
                    elif path[i][0] == (path[i+1][0] -1) :
                        self.qLearningTable[(path[i][0], path[i][1])][2] = (0.9 * self.rewards[path[i+1][0]][path[i+1][1]])
                        self.rewards[path[i][0]][path[i][1]] = (0.9 * self.rewards[path[i+1][0]][path[i+1][1]])
                    elif path[i][0] == (path[i+1][0] +1) :
                        self.qLearningTable[(path[i][0], path[i][1])][3] = (0.9 * self.rewards[path[i+1][0]][path[i+1][1]])
                        self.rewards[path[i][0]][path[i][1]] = (0.9 * self.rewards[path[i+1][0]][path[i+1][1]])

    def initializeTable(self):
        lista_aux = [(0,0),(0,1),(0,1),(0,2),(0,3),(0,4),(1,0),(1,4),(2,0),(2,4),(3,0),(3,4),(4,4),
        (4,0),(5,0),(5,4),(6,0),(6,4),(7,0),(7,1),(7,2),(7,3)]
        for x in range(self.maxCoord[0]):
            for y in range(self.maxCoord[1]):
                if (x,y) not in lista_aux:
                    self.qLearningTable[(x,y)] = [0,0,0,0]
        self.qLearningTable[self.getGoalPosition()] = [100,100,100,100]
        
    def addServerQtableArrows(self):
        lista_aux = [self.getGoalPosition(),self.getSelfPosition()]
        for x, y in self.qLearningTable:
            if (x,y) not in lista_aux:
                aux = self.qLearningTable[(x,y)].index(max(self.qLearningTable[(x,y)]))
                self.markArrow(aux, x, y)




def main():
    agent = Agent()
    if agent.getConnection() != -1:
        estados = ["north", "east", "west", "south"]
        aux = 0
        goalPosition = agent.getGoalPosition()
        obstacles = agent.getObstacles()
        path = []
        rewards = agent.getRewards()
        agent.initializeTable()
        #estado_anterior = None
        interactions = 5
        while aux != interactions:
            estado = random.randint(0,3)
            """
            if previous_estado != estado:
                if estado == 0:
                    previous_estado = 3
                elif estado == 1:
                    previous_estado = 2
                elif estado == 2:
                    previous_estado = 1
                elif estado == 3:
                    previous_estado = 0   
            """ 
            agent.c.execute("command", estados[estado])
            path.append(agent.getSelfPosition())
            if agent.getSelfPosition() == goalPosition:
                agent.c.execute("command", "home")
                agent.updateQLearningTable(path)
                path = []
                aux += 1
        q_table = agent.get_q_table()
        print("QTable:\n\n" + str(q_table))
        agent.addServerQtableArrows()
        input("Press to Stop")
    
if __name__ == "__main__":
    main()
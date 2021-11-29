from __future__ import print_function, unicode_literals
from PyInquirer import prompt
from bparser import Parser
from graph import Graph
from sumo import SumoGenerator
from __env__ import BP_SMALL, BP_MEDIUM, BP_LARGE
from random import randint
import time
import sys
from threading import Thread, Event


class Inquirer():
    def __init__(self) -> None:
        self.blueprints = [BP_SMALL, BP_MEDIUM, BP_LARGE]

        self.lists = {
            "blueprint": ["Small", "Medium", "Big"],
            "action": [
                "Visualize the parking lot state", 
                "Get intelligent routing",
                "Generate Sumo simulation"
            ],
            "routing": [
                "Get new free spot from entrance",
                "Get new free spot",
                "Find the exit",
            ]
        }

        self.questions = [
            {
                'type': 'list',
                'name': 'blueprint',
                'message': 'Select the blueprint:',
                'choices': self.lists["blueprint"],
                'filter': lambda val: self.__get_graph(val)
            },
            {
                'type': 'list',
                'name': 'action',
                'message': 'Select the action:',
                'choices': self.lists["action"],
                'filter': lambda val: self.lists["action"].index(val)
            },
            {
                'type': 'confirm',
                'name': 'disabled',
                'message': 'Is this concerning disabled people?',
                'default': False,
            },
            {
                'type': 'list',
                'name': 'routing',
                'message': 'Select the action:',
                'choices': self.lists["routing"],
                'filter': lambda val: self.lists["routing"].index(val)
            },
            {
                'type': 'confirm',
                'name': 'exit',
                'message': 'Do you want to exit?',
                'default': False,
            },
        ]


    def inquire(self) -> None:
        """ 
        Prompts the user with the questions
        """

        ext = False
        while not ext:
            answers = prompt(self.questions[:2])
            self.graph = answers["blueprint"]
            self.__perform_action(answers["action"])

            ext = prompt(self.questions[4])["exit"]


    """ Private Methods """


    def __perform_action(self, action: int) -> None:
        """ 
        Either draws the graph, provides intelligent routing or Sumo simulates the parking lot
        """

        if action == 0:
            self.graph.draw(None, True)
        elif action == 1:
            answers = prompt(self.questions[2:4])
            is_disabled = answers["disabled"]
            action = answers["routing"]
            try:
                if action == 0 or action == 1:
                    snode = self.graph.get_random_occupied_spot(is_disabled) if action == 1 else self.graph.entrance
                    node, path = self.graph.get_nearest_free_spot(snode, is_disabled, False)
                    if is_disabled and node is None:
                        node, path = self.graph.get_nearest_free_spot(snode, False, False)
                    node.free = False
                    self.graph.draw(path)
                elif action == 2:
                    dst, path = self.graph.get_path(self.graph.get_random_occupied_spot(is_disabled), self.graph.exit, False)
                    path[0].free = False
                    self.graph.draw(path)
            except Exception as e:
                self.graph.draw(None, True)
        elif action == 2:
            s = SumoGenerator(self.graph)
            s.generate_nodes_xml()
            s.generate_edges_xml()            
            s.generate_routes_xml(s.generate_random_routes())
    

    def __get_graph(self, val: str) -> Graph:
        """ 
        Gets the chosen graph, parses it and creates the Graph instance
        """

        blueprint = self.blueprints[self.lists["blueprint"].index(val)]
        exit_event = Event()
        thread = Thread(target=Inquirer.__show_progress_bar, args=(exit_event,))
        thread.start()
        p = Parser(blueprint)
        g = Graph(p)
        g.generate_random_state(randint(0,90) / 100.0, randint(0,90) / 100.0)
        exit_event.set()
        thread.join()
        return g


    def __show_progress_bar(exit_event: Event) -> None:
        """ 
        Prints the graph parsing progress bar
        """

        i = 0
        while True:
            time.sleep(1)
            sys.stdout.write(f"\rLoading the graph" + "." * (i%3 +1) + " " * (3 - i%3 + 1))
            sys.stdout.flush()
            i += 1
            if exit_event.is_set():
                sys.stdout.write("\r")
                sys.stdout.flush()
                break


    

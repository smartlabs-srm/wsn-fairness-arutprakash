import subprocess
import sys

try:
    import pydot

    has_pydot = True
except ImportError:
    has_pydot = False


class LoLADraw:

    def get_net(self, filename):

        places = []
        markings = {}
        transitions = {}

        place_mode = False
        marking_mode = False
        transition_mode = False

        trans_consume_mode = True
        trans_name = ""
        trans_consume = {}
        trans_produce = {}

        with open(filename) as f:

            for line in f:
                if "PLACE" in line:
                    place_mode = True
                    continue
                elif "MARKING" in line:
                    place_mode = False
                    marking_mode = True
                    continue
                elif "TRANSITION" in line:
                    marking_mode = False
                    transition_mode = True

                line = line.strip()
                if not line:
                    continue

                print(line)
                if place_mode:
                    if "SAFE" in line:
                        continue
                    for place in line.split(','):
                        place = place.replace(";", "").strip()
                        if place:
                            places.append(place)
                elif marking_mode:
                    for marking in line.split(','):
                        if not marking:
                            continue
                        m = marking.split(":")
                        markings[m[0].strip()] = m[1].replace(";", "").strip()
                elif transition_mode:
                    if "TRANSITION" in line:

                        if trans_name:
                            transitions[trans_name] = (trans_consume, trans_produce)
                            trans_consume = {}
                            trans_produce = {}

                        trans_name = line.split(" ")[1]

                    elif trans_consume_mode:

                        if "CONSUME" in line:
                            continue
                        elif "PRODUCE" in line:
                            trans_consume_mode = False
                        else:
                            for consume in line.split(","):
                                if not consume:
                                    continue
                                place, marking = consume.split(":")
                                trans_consume[place.strip()] = marking.replace(";", "").strip()
                    elif not trans_consume_mode:
                        if ";" in line:
                            trans_consume_mode = True
                        for produce in line.split(","):
                            if not produce:
                                continue
                            place, marking = produce.split(":")
                            trans_produce[place.strip()] = marking.replace(";", "").strip()

            # do end-of-file
            if trans_name:
                transitions[trans_name] = (trans_consume, trans_produce)
        return places, markings, transitions

    def draw(self, filename):

        name = filename.replace(".lola", "")
        nodes = {}
        graph = pydot.Dot(name, graph_type='digraph', layout='fdp')

        places, markings, transitions = self.get_net(filename)
        print("Places: " + str(places))
        print("Markings: " + str(markings))
        print("Transitions: " + str(transitions))

        for i, place in enumerate(places):
            v_attr = place
            if place in markings:
                v_attr += "\n" + markings[place]

            nodes[place] = pydot.Node(v_attr, style="filled", fillcolor='lightblue')
            graph.add_node(nodes[place])

        for t_name, _ in transitions.items():
            v_attr = t_name

            nodes[t_name] = pydot.Node(v_attr, style="filled")
            graph.add_node(nodes[t_name])

        for t_name, conpro in transitions.items():
            c, p = conpro

            for c_name, weight in c.items():
                graph.add_edge(pydot.Edge(nodes[c_name], nodes[t_name]))  # , color=color))

            for p_name, weight in p.items():
                graph.add_edge(pydot.Edge(nodes[t_name], nodes[p_name], label=weight))
                # , color=color))

        dot_filename = filename.replace(".lola", ".dot")
        graph.write(dot_filename, prog='dot')

        svg_filename = filename.replace(".lola", ".svg")
        command = "dot -Tsvg " + dot_filename + " -o " + svg_filename
        returncode = subprocess.call(command, shell=True)
        if returncode != 0:
            print("ERROR: Please ensure that GraphViz is installed!")

        print("Exported drawing to file: " + svg_filename)
        # command = "rm " + dot_filename
        # subprocess.call(command, shell=True)


if __name__ == "__main__":

    print("Starting LoLADraw...")
    if len(sys.argv) < 2:
        print("Error: Please pass a filename as the first argument.")
        exit(1)

    if not has_pydot:
        print("ERROR: Install pydot first!")
        exit(1)

    filename = sys.argv[1]
    ld = LoLADraw()
    ld.draw(filename)

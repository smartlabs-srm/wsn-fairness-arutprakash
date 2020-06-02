import sys
import xml.etree.ElementTree as ET


class LoLAConvert:

    def __init__(self):
        # TODO:
        # - Add capacity
        # - Prevent inhibitors
        pass

    def convert_file(self, filename):

        places, transitions, arcs = self.parse_pnml(filename)

        print("Places: ")
        for p, v in places.items():
            print(str(p) + " : " + str(v))

        print("Transitions: ")
        for t, v in transitions.items():
            print(str(t) + ",")# + str(v))

        print("Arcs: ")
        for a in arcs:
            print(a)

        places_with_markings = []
        for p_id, p_data in places.items():
            p_name, marking = p_data
            if int(marking) > 0:
                places_with_markings.append((p_id, p_name, marking))

        lola_file = filename.replace(".xml", ".lola")
        with open(lola_file, 'w') as f:
            f.write("PLACE\n")

            for i, p_id in enumerate(places):
                p_name, marking = places[p_id]
                f.write("\t" + p_name)
                if i < len(places) - 1:
                    f.write(",\n")
                else:
                    f.write(";\n")

            f.write("\nMARKING\n")
            for i, pm in enumerate(places_with_markings):
                f.write("\t" + pm[1] + " : " + pm[2])
                if i < len(places_with_markings) - 1:
                    f.write(",\n")
                else:
                    f.write(";\n")

            for trans_id, trans_name in transitions.items():
                f.write("\nTRANSITION " + trans_name + "\n")
                consume = {}
                produce = {}

                for arc in arcs:
                    s, t, w = arc
                    if t == trans_id:
                        consume[s] = w
                    elif s == trans_id:
                        produce[t] = w

                f.write("\tCONSUME\n")
                if len(consume) == 0:
                    f.write(";\n")

                for i, s in enumerate(consume):
                    f.write("\t\t" + places[s][0] + " : " + consume[s])
                    if i < len(consume) - 1:
                        f.write(",\n")
                    else:
                        f.write(";\n")
                f.write("\tPRODUCE\n")
                if len(produce) == 0:
                    f.write(";\n")

                for i, t in enumerate(produce):
                    f.write("\t\t" + places[t][0] + " : " + produce[t])
                    if i < len(produce) - 1:
                        f.write(",\n")
                    else:
                        f.write(";\n")

        print("Wrote to: " + str(lola_file))

    def parse_pnml(self, filename):
        tree = ET.parse(filename)
        root = tree.getroot()
        net = root[0]

        places = {}
        transitions = {}
        arcs = []

        for child in net:

            if child.tag == "place":
                p_id = child.get("id")

                name_node = self.get_child_with_name(child, "name")
                name = self.get_child_with_name(name_node, "value").text
                name = name.replace(" ", ".")

                marking_node = self.get_child_with_name(child, 'initialMarking')
                marking_value_node = self.get_child_with_name(marking_node, 'value')
                marking = marking_value_node.text.split(",")[1]

                places[p_id] = (name, marking)

            elif child.tag == "transition":
                t_id = child.get("id")

                name_node = self.get_child_with_name(child, "name")
                name = self.get_child_with_name(name_node, "value").text
                name = name.replace(" ", ".")

                transitions[t_id] = name

            elif child.tag == "arc":
                source = child.get("source")
                target = child.get("target")

                inscription_node = self.get_child_with_name(child, 'inscription')
                inscription_value_node = self.get_child_with_name(inscription_node, 'value')
                inscription = inscription_value_node.text.split(",")[1]

                arcs.append((source, target, inscription))

        return places, transitions, arcs

    def get_child_with_name(self, node, name):
        for child in node:
            if child.tag == name:
                return child
        raise Exception("On node: " + str(node) + ", the child " + name + " was not found!")


if __name__ == "__main__":

    print("Starting LoLAConvert...")
    if len(sys.argv) < 2:
        print("Error: Please pass a filename as the first argument.")
        exit(1)

    filename = sys.argv[1]
    lc = LoLAConvert()
    lc.convert_file(filename)

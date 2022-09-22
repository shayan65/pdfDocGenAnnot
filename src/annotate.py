class Annotate:
    def __init__(self, label,class_label, wi, hi):
        self.label = label
        self.class_label=class_label
        self.wi = wi
        self.hi = hi
        
    def annot(self):
        (c1,c2)=(round(0.5*(float(self.label["xMin"])+float(self.label["xMax"]))/self.wi, 6),
                 round(0.5*(float(self.label["yMin"])+float(self.label["yMax"]))/self.hi, 6))
        (w,h) = (round(abs(float(self.label["xMax"])-float(self.label["xMin"]))/self.wi, 6),
                 round(abs(float(self.label["xMax"])-float(self.label["xMin"]))/self.hi,6))
                 
        line =      [
                    self.class_label,
                    str(c1) ,
                    str(c2) ,
                    str(w)  ,
                    str(h)  
                    ]
        print("line", line)
        return " ".join(line)
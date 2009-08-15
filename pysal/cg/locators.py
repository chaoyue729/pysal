"""
Computational geometry code for PySAL: Python Spatial Analysis Library.

Authors:
Sergio Rey <srey@asu.edu>
Xinyue Ye <xinyue.ye@gmail.com>
Charles Schmidt <Charles.Schmidt@asu.edu>
Andrew Winslow <Andrew.Winslow@asu.edu>

Not to be used without permission of the authors. 

Style Guide, Follow:
http://www.python.org/dev/peps/pep-0008/


Class comment format:

    Brief class description.

    Attributes:
    attr 1 -- type -- description of attr 1
    attr 2 -- type -- description of attr 2

    Extras (notes, references, examples, doctest, etc.)


Function comment format:

    Brief function description.

    function(arg 1 type, arg 2 type, keyword=keyword arg 3 type) -> return type

    Argument:
    arg 1 -- description of arg 1
    arg 2 -- description of arg 2

    Keyword Arguments:
    arg 3 -- description of arg 3

    Extras (notes, references, examples, doctest, etc.)
"""

__author__  = "Sergio J. Rey, Xinyue Ye, Charles Schmidt, Andrew Winslow"
__credits__ = "Copyright (c) 2005-2009 Sergio J. Rey"

import math
import copy
import doctest
from standalone import *
from shapes import *

class IntervalTree:
    """
    Representation of an interval tree. An interval tree is a data structure which is used to
    quickly determine which intervals in a set contain a value or overlap with a query interval.

    Reference:
    de Berg, van Kreveld, Overmars, Schwarzkopf. Computational Geometry: Algorithms and Application. 
    212-217. Springer-Verlag, Berlin, 2000.
    """

    class Node:
        """
        Private class representing a node in an interval tree.
        """

        def __init__(self, val, left_list, right_list, left_node, right_node):
            self.val = val
            self.left_list = left_list
            self.right_list = right_list
            self.left_node = left_node
            self.right_node = right_node

        def query(self, q):
            i = 0
            if q < self.val:
                while i < len(self.left_list) and self.left_list[i][0] <= q:
                    i += 1
                return [rec[2] for rec in self.left_list[0:i]]
            else:
                while i < len(self.right_list) and self.right_list[i][1] >= q:
                    i += 1
                return [rec[2] for rec in self.right_list[0:i]]

        def add(self, i):
            """
            Adds an interval to the IntervalTree node.
            """
            if not i[0] <= self.val <= i[1]:
                raise Exception, 'Attempt to add an interval to an inappropriate IntervalTree node'
            index = 0
            while index < len(self.left_list) and self.left_list[index] < i[0]:
                index = index + 1
            self.left_list.insert(index, i)
            index = 0
            while index < len(self.right_list) and self.right_list[index] > i[1]:
                index = index + 1
            self.right_list.insert(index, i)

        def remove(self, i):
            """
            Removes an interval from the IntervalTree node.
            """
            l = 0
            r = len(self.left_list)
            while l < r:
                m = (l + r)/2
                if self.left_list[m] < i[0]:
                    l = m + 1
                elif self.left_list[m] > i[0]:
                    r = m
                else:
                    if self.left_list[m] == i:
                        self.left_list.pop(m)
                    else:
                        raise Exception, 'Attempt to remove an unknown interval'
            l = 0
            r = len(self.right_list)
            while l < r:
                m = (l + r)/2
                if self.right_list[m] > i[1]:
                    l = m + 1
                elif self.right_left[m] < i[1]:
                    r = m
                else:
                    if self.right_list[m] == i:
                        self.right_list.pop(m)
                    else:
                        raise Exception, 'Attempt to remove an unknown interval'

    def __init__(self, intervals):
        """
        Returns an interval tree containing specified intervals.

        __init__((number, number, x) list) -> IntervalTree

        Arguments:
        intervals -- a list of (lower, upper, item) elements to build the interval tree with

        Example:
        >>> intervals = [(-1, 2, 'A'), (5, 9, 'B'), (3, 6, 'C')]
        >>> it = IntervalTree(intervals)
        >>> isinstance(it, IntervalTree)
        True
        """
        self._build(intervals)

    def _build(self, intervals):
        """
        Build an interval tree containing _intervals_.
        Each interval should be of the form (start, end, object).

        build((number, number, x) list) -> None

        Test tag: <tc>#is#IntervalTree.build</tc>
        """
        bad_is = filter(lambda i: i[0] > i[1], intervals)
        if bad_is != []:
            raise Exception, 'Attempt to build IntervalTree with invalid intervals: ' + str(bad_is)
        eps = list(set([i[0] for i in intervals] + [i[1] for i in intervals]))
        eps.sort()
        self.root = self._recursive_build(copy.copy(intervals), eps)

    def query(self, q):
        """
        Returns the intervals intersected by a value or interval.

        query((number, number) or number) -> x list

        Arguments:
        q -- a value or interval to find intervals intersecting

        Example:
        >>> intervals = [(-1, 2, 'A'), (5, 9, 'B'), (3, 6, 'C')]
        >>> it = IntervalTree(intervals)
        >>> it.query((7, 14))
        ['B']
        >>> it.query(1)
        ['A']
        """
        if isinstance(q, tuple):
            return self._query_range(q, self.root)
        else:
            return self._query_points(q)

    def _query_range(self, q, root):
        if root == None:
            return []
        if root.val < q[0]:
            return self._query_range(q, root.right_node) + root.query(q[0])
        elif root.val > q[1]:
            return self._query_range(q, root.left_node) + root.query(q[1])
        else:
            return root.query(root.val) + self._query_range(q, root.left_node) + self._query_range(q, root.right_node)

    def _query_points(self, q):
        found = []
        cur = self.root
        while cur != None:
            found.extend(cur.query(q))
            if q < cur.val:
                cur = cur.left_node
            else:
                cur = cur.right_node
        return found


    def _recursive_build(self, intervals, eps):
        def sign(x):
            if x < 0:
                return -1
            elif x > 0:
                return 1
            else:
                return 0

        def binary_search(list, q):
            l = 0
            r = len(list)
            while l < r:
                m = (l + r)/2
                if list[m] < q:
                    l = m + 1
                else:
                    r = m
            return l

        if eps == []:
            return None
        median = eps[len(eps)/2]
        hit_is = []
        rem_is = []
        for i in intervals:
            if i[0] <= median <= i[1]:
                hit_is.append(i)
            else:
                rem_is.append(i)
        left_list = copy.copy(hit_is)
        left_list.sort(lambda a, b: sign(a[0] - b[0]))
        right_list = copy.copy(hit_is)
        right_list.sort(lambda a, b: sign(b[1] - a[1]))
        eps = list(set([i[0] for i in intervals] + [i[1] for i in intervals]))
        eps.sort()
        bp = binary_search(eps, median)
        left_eps = eps[:bp]
        right_eps = eps[bp:]
        node = (IntervalTree.Node(median, left_list, right_list,
                    self._recursive_build(rem_is, left_eps),
                    self._recursive_build(rem_is, right_eps)))
        return node

class Grid:
    """
    Representation of a binning data structure.
    """

    def __init__(self, bounds, resolution):
        """
        Returns a grid with specified properties. 

        __init__(Rectangle, number) -> Grid 

        Arguments:
        bounds -- the area for the grid to encompass
        resolution -- the diameter of each bin 

        Example:
        >>> g = Grid(Rectangle(0, 0, 10, 10), 1)
        """
        if resolution == 0:
            raise Exception, 'Cannot create grid with resolution 0'
        self.res = resolution
        self.hash = {}
        self.x_range = (bounds.left, bounds.right)
        self.y_range = (bounds.lower, bounds.upper)
        try:
            self.i_range = int(math.ceil((self.x_range[1]-self.x_range[0])/self.res))
            self.j_range = int(math.ceil((self.y_range[1]-self.y_range[0])/self.res))
        except Exception:
            raise Exception, ('Invalid arguments for Grid(): (' +
                                 str(x_range) + ', ' + str(y_range) + ', ' + str(res) + ')')

    def in_grid(self, loc):
        """
        Returns whether a 2-tuple location _loc_ lies inside the grid bounds.
        
        Test tag: <tc>#is#Grid.in_grid</tc>
        """
        return (self.x_range[0] <= loc[0] <= self.x_range[1] and
                self.y_range[0] <= loc[1] <= self.y_range[1])

    def __grid_loc(self, loc):
        i = min(self.i_range, max(int((loc[0] - self.x_range[0])/self.res), 0))
        j = min(self.j_range, max(int((loc[1] - self.y_range[0])/self.res), 0))
        return (i, j)

    def add(self, item, pt):
        """
        Adds an item to the grid at a specified location.

        add(x, Point) -> x

        Arguments:
        item -- the item to insert into the grid
        pt -- the location to insert the item at

        >>> g = Grid(Rectangle(0, 0, 10, 10), 1)
        >>> g.add('A', Point((4.2, 8.7)))
        'A'
        """
        if not self.in_grid(pt):
            raise Exception, 'Attempt to insert item at location outside grid bounds: ' + str(pt)
        grid_loc = self.__grid_loc(pt)
        if grid_loc in self.hash:
            self.hash[grid_loc].append((pt, item))
        else:
            self.hash[grid_loc] = [(pt, item)]
        return item

    def remove(self, item, pt):
        """
        Removes an item from the grid at a specified location.

        remove(x, Point) -> x

        Arguments:
        item -- the item to remove from the grid
        pt -- the location the item was added at

        >>> g = Grid(Rectangle(0, 0, 10, 10), 1)
        >>> g.add('A', Point((4.2, 8.7)))
        'A'
        >>> g.remove('A', Point((4.2, 8.7)))
        'A'
        """
        if not self.in_grid(pt):
            raise Exception, 'Attempt to remove item at location outside grid bounds: ' + str(pt)
        grid_loc = self.__grid_loc(pt)
        self.hash[grid_loc].remove((pt, item))
        if self.hash[grid_loc] == []:
            del self.hash[grid_loc]
        return item

    def bounds(self, bounds):
        """
        Returns a list of items found in the grid within the bounds specified.

        bounds(Rectangle) -> x list

        Arguments:
        item -- the item to remove from the grid
        pt -- the location the item was added at

        >>> g = Grid(Rectangle(0, 0, 10, 10), 1)
        >>> g.add('A', Point((1.0, 1.0)))
        'A'
        >>> g.add('B', Point((4.0, 4.0)))
        'B'
        >>> g.bounds(Rectangle(0, 0, 3, 3))
        ['A']
        >>> g.bounds(Rectangle(2, 2, 5, 5))
        ['B']
        >>> sorted(g.bounds(Rectangle(0, 0, 5, 5)))
        ['A', 'B']
        """
        x_range = (bounds.left, bounds.right)
        y_range = (bounds.lower, bounds.upper)
        items = []
        lower_left = self.__grid_loc((x_range[0], y_range[0]))
        upper_right = self.__grid_loc((x_range[1], y_range[1]))
        for i in xrange(lower_left[0], upper_right[0] + 1):
            for j in xrange(lower_left[1], upper_right[1] + 1):
                if (i, j) in self.hash:
                    items.extend(map(lambda item: item[1], filter(lambda item: x_range[0] <= item[0][0] <= x_range[1] and y_range[0] <= item[0][1] <= y_range[1], self.hash[(i,j)])))
        return items

    def proximity(self, pt, r):
        """
        Returns a list of items found in the grid within a specified distance of a point.

        proximity(Point, number) -> x list

        Arguments:
        pt -- the location to search around
        r -- the distance to search around the point

        >>> g = Grid(Rectangle(0, 0, 10, 10), 1)
        >>> g.add('A', Point((1.0, 1.0)))
        'A'
        >>> g.add('B', Point((4.0, 4.0)))
        'B'
        >>> g.proximity(Point((2.0, 1.0)), 2)
        ['A']
        >>> g.proximity(Point((6.0, 5.0)), 3.0)
        ['B']
        >>> sorted(g.proximity(Point((4.0, 1.0)), 4.0))
        ['A', 'B']
        """
        items = []
        lower_left = self.__grid_loc((pt[0] - r, pt[1] - r))
        upper_right = self.__grid_loc((pt[0] + r, pt[1] + r))
        for i in xrange(lower_left[0], upper_right[0] + 1):
            for j in xrange(lower_left[1], upper_right[1] + 1):
                if (i, j) in self.hash:
                    items.extend(map(lambda item: item[1], filter(lambda item: get_points_dist(pt, item[0]) <= r, self.hash[(i,j)])))
        return items

    def nearest(self, pt):
        """
        Returns the nearest item to a point.

        nearest(Point) -> x 

        Arguments:
        pt -- the location to search near

        >>> g = Grid(Rectangle(0, 0, 10, 10), 1)
        >>> g.add('A', Point((1.0, 1.0)))
        'A'
        >>> g.add('B', Point((4.0, 4.0)))
        'B'
        >>> g.nearest(Point((2.0, 1.0)))
        'A'
        >>> g.nearest(Point((7.0, 5.0)))
        'B'
        """
        search_size = self.res
        while (self.proximity(pt, search_size) == [] and
               (get_points_dist((self.x_range[0], self.y_range[0]), pt) > search_size or
                get_points_dist((self.x_range[1], self.y_range[0]), pt) > search_size or
                get_points_dist((self.x_range[0], self.y_range[1]), pt) > search_size or
                get_points_dist((self.x_range[1], self.y_range[1]), pt) > search_size)):
            search_size = 2*search_size
        items = []
        lower_left = self.__grid_loc((pt[0] - search_size, pt[1] - search_size))
        upper_right = self.__grid_loc((pt[0] + search_size, pt[1] + search_size))
        for i in xrange(lower_left[0], upper_right[0] + 1):
            for j in xrange(lower_left[1], upper_right[1] + 1):
                if (i, j) in self.hash:
                    items.extend(map(lambda item: (get_points_dist(pt, item[0]), item[1]), self.hash[(i,j)]))
        if items == []:
            return None
        return min(items)[1]

class BruteForcePointLocator:
    """
    A class which does naive linear search on a set of Point objects.
    """
    def __init__(self, points):
        """
        Creates a naive index of the points specified.

        __init__(Point list) -> BruteForcePointLocator

        Arguments:
        points -- a list of points to index (Point list)
       
        Example:
        >>> pl = BruteForcePointLocator([Point((0, 0)), Point((5, 0)), Point((0, 10))])
        """
        self._points = points

    def nearest(self, query_point):
        """
        Returns the nearest point indexed to a query point.
 
        nearest(Point) -> Point

        Arguments:
        query_point -- a point to find the nearest indexed point to

        >>> points = [Point((0, 0)), Point((1, 6)), Point((5.4, 1.4))]
        >>> pl = BruteForcePointLocator(points)
        >>> n = pl.nearest(Point((1, 1)))
        >>> str(n)
        '(0.0, 0.0)'
        """ 
        return min(self._points, key=lambda p: get_points_dist(p, query_point))

    def region(self, region_rect):
        """
        Returns the indexed points located inside a rectangular query region.
 
        region(Rectangle) -> Point list

        Arguments:
        region_rect -- the rectangular range to find indexed points in

        Example:
        >>> points = [Point((0, 0)), Point((1, 6)), Point((5.4, 1.4))]
        >>> pl = BruteForcePointLocator(points)
        >>> pts = pl.region(Rectangle(-1, -1, 10, 10))
        >>> len(pts)
        3
        """
        return filter(lambda p: get_rectangle_point_intersect(region_rect, p) != None, self._points)

    def proximity(self, origin, r):
        """
        Returns the indexed points located within some distance of an origin point.
 
        proximity(Point, number) -> Point list

        Arguments:
        origin -- the point to find indexed points near
        r -- the maximum distance to find indexed point from the origin point

        Example:
        >>> points = [Point((0, 0)), Point((1, 6)), Point((5.4, 1.4))]
        >>> pl = BruteForcePointLocator(points)
        >>> neighs = pl.proximity(Point((1, 0)), 2)
        >>> len(neighs)
        1
        >>> p = neighs[0]
        >>> isinstance(p, Point)
        True
        >>> str(p)
        '(0.0, 0.0)'
        """
        return filter(lambda p: get_points_dist(p, origin) <= r, self._points) 

class PointLocator:
    """
    An abstract representation of a point indexing data structure.
    """ 

    def __init__(self, points):
        """
        Returns a point locator object.

        __init__(Point list) -> PointLocator
  
        Arguments:
        points -- a list of points to index

        Example:
        >>> points = [Point((0, 0)), Point((1, 6)), Point((5.4, 1.4))]
        >>> pl = PointLocator(points)
        """
        self._locator = BruteForcePointLocator(points)

    def nearest(self, query_point):
        """
        Returns the nearest point indexed to a query point.
 
        nearest(Point) -> Point

        Arguments:
        query_point -- a point to find the nearest indexed point to

        Example:
        >>> points = [Point((0, 0)), Point((1, 6)), Point((5.4, 1.4))]
        >>> pl = PointLocator(points)
        >>> n = pl.nearest(Point((1, 1)))
        >>> str(n)
        '(0.0, 0.0)'
        """
        return self._locator.nearest(query_point)

    def region(self, region_rect):
        """
        Returns the indexed points located inside a rectangular query region.
 
        region(Rectangle) -> Point list

        Arguments:
        region_rect -- the rectangular range to find indexed points in

        Example:
        >>> points = [Point((0, 0)), Point((1, 6)), Point((5.4, 1.4))]
        >>> pl = PointLocator(points)
        >>> pts = pl.region(Rectangle(-1, -1, 10, 10))
        >>> len(pts)
        3
        """
        return self._locator.region(region_rect)
   
    def proximity(self, origin, r):
        """
        Returns the indexed points located within some distance of an origin point.
 
        proximity(Point, number) -> Point list

        Arguments:
        origin -- the point to find indexed points near
        r -- the maximum distance to find indexed point from the origin point

        Example:
        >>> points = [Point((0, 0)), Point((1, 6)), Point((5.4, 1.4))]
        >>> pl = PointLocator(points)
        >>> len(pl.proximity(Point((1, 0)), 2))
        1
        """
        return self._locator.proximity(origin, r)

class PolygonLocator:
    """
    An abstract representation of a polygon indexing data structure.
    """ 

    def __init__(self, polygons):
        """
        Returns a polygon locator object.

        __init__(Polygon list) -> PolygonLocator
  
        Arguments:
        polygons -- a list of polygons to index

        Example:
        >>> p1 = Polygon(points=[Point((0, 1)), Point((4, 5)), Point((5, 1))])
        >>> p2 = Polygon(points=[Point((3, 9)), Point((6, 7)), Point((1, 1))])
        >>> pl = PolygonLocator([p1, p2])
        >>> isinstance(pl, PolygonLocator)
        True
        """
        pass

    def nearest(self, query_point):
        """
        Returns the nearest polygon indexed to a query point.
 
        nearest(Polygon) -> Polygon

        Arguments:
        query_point -- a point to find the nearest indexed polygon to

        Example:
        >>> p1 = Polygon(points=[Point((0, 1)), Point((4, 5)), Point((5, 1))])
        >>> p2 = Polygon(points=[Point((3, 9)), Point((6, 7)), Point((1, 1))])
        >>> pl = PolygonLocator([p1, p2])
        >>> n = pl.nearest(Point((-1, 1)))
        >>> str(min(n.vertices()))
        (0.0, 1.0)
        """
        pass

    def region(self, region_rect):
        """
        Returns the indexed polygons located inside a rectangular query region.
 
        region(Rectangle) -> Polygon list

        Arguments:
        region_rect -- the rectangular range to find indexed polygons in

        Example:
        >>> p1 = Polygon(points=[Point((0, 1)), Point((4, 5)), Point((5, 1))])
        >>> p2 = Polygon(points=[Point((3, 9)), Point((6, 7)), Point((1, 1))])
        >>> pl = PolygonLocator([p1, p2])
        >>> n = pl.region(Rectangle(0, 0, 4, 10))
        >>> len(n)
        2
        """
        pass

    def proximity(self, origin, r):
        """
        Returns the indexed polygons located within some distance of an origin point.
 
        proximity(Polygon, number) -> Polygon list

        Arguments:
        origin -- the point to find indexed polygons near
        r -- the maximum distance to find indexed polygon from the origin point

        Example:
        >>> p1 = Polygon(points=[Point((0, 1)), Point((4, 5)), Point((5, 1))])
        >>> p2 = Polygon(points=[Point((3, 9)), Point((6, 7)), Point((1, 1))])
        >>> pl = PolygonLocator([p1, p2])
        >>> len(pl.proximity(Point((0, 0)), 2))
        2
        """
        pass


def _test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    _test()




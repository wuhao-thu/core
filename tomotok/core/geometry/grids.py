# Copyright 2021 Institute of Plasma Physics of the Czech Academy of Sciences. 
#
# Licensed under the EUPL-1.2 or later.
"""
Contains class describing regularly spaced node grid
"""
import numpy as np
from matplotlib.path import Path


class RegularGrid(object):
    """
    Rectangular grid of regularly spaced rectangles of same size

    Describes rectangular reconstruction grid consisting of regularly spaced toroidally szmmetric nodes
    that have rectangular projection to reconstruction plane.

    Attributes
    ----------
    nr : int
        number of nodes along r (radial) axis
    nz : int
        number of nodes along z (vertical) axis
    nodes_num : int
        total number of nodes
    rmin, rmax : float
        limits of r axis
    zmin, zmax : float
        limits of z axis
    dr, dz : float
        dimension of node in r or z axis
    r_border, z_border : numpy.ndarray
        arrays containing r resp. z coordinates of node borders
    r_center, z_center : numpy.ndarray
        arrays containing r resp. z coordinates of node centers
    nodevol : numpy.ndarray
        Array containing volumes of nodes (voxel) with shape (nz, nr)
    """

    def __init__(self, nr, nz, rlims, zlims):
        """
        Parameters
        ----------
        nr : int
            number of nodes along radial axis r
        nz : int
            number of nodes along vertical axis z
        rlims : tuple of float
            limits of r axis, (min, max)
        zlims : tuple of float
            limits of z axis, (min, max)
        """
        self.nr = nr
        self.nz = nz
        self.nodes_num = self.size
        self.rmin = rlims[0]
        self.rmax = rlims[1]
        self.zmin = zlims[0]
        self.zmax = zlims[1]
        self.dr = (self.rmax - self.rmin) / self.nr
        self.dz = (self.zmax - self.zmin) / self.nz
        self.r_border = np.linspace(self.rmin, self.rmax, self.nr + 1)
        self.z_border = np.linspace(self.zmin, self.zmax, self.nz + 1)
        self.r_center = self.r_border[:-1] + self.dr / 2
        self.z_center = self.z_border[:-1] + self.dz / 2
        return

    @property
    def nodevol(self):
        """
        Volumes of individual nodes

        Returns
        -------
        numpy.ndarray
            matrix with volume values for each node with shape (nz, nr)
        """
        nodevol_r = 2 * np.pi * self.dr * self.dz * self.r_center
        nodevol = np.ones((self.nz, self.nr)) * nodevol_r
        return nodevol

    @property
    def centre(self):
        return (self.rmax + self.rmin)/2, (self.zmax + self.zmin)/2

    @property
    def extent(self):
        """
        Grid extent in format for use in matplotlib

        Returns
        -------
        tuple of floats
            rmin, rmax, zmin, zmax
        """
        return self.rmin, self.rmax, self.zmin, self.zmax

    @property
    def size(self):
        return self.nr * self.nz

    @property
    def shape(self):
        return self.nz, self.nr

    @property
    def center_mesh(self):
        return np.meshgrid(self.r_center, self.z_center)

    def __repr__(self):
        msg = 'Node grid with resolution {}h{}'.format(self.nr, self.nz)
        msg += ' and bounds ({};{})r, ({};{})z.'.format(*self.extent)
        return msg

    def is_inside(self, r, z):
        """
        Determines whether node centers are inside given polygon.

        Parameters
        ----------
        r, z : numpy.ndarray
            Coordinate vectors of polygon

        Returns
        -------
        numpy.ndarray
            Mask matrix for pixgrid with True values for nodes inside polygon
        """
        rm, zm = np.meshgrid(self.r_center, self.z_center)
        rm, zm = rm.flatten(), zm.flatten()
        points = np.stack((rm, zm), axis=1)
        limiter_coords = np.stack((r, z), axis=1)
        p = Path(limiter_coords)
        grid_points = p.contains_points(points)
        inside = grid_points.reshape(self.shape)
        return inside

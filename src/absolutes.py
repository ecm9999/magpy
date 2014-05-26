#!/usr/bin/env python
"""
MagPy-absolutes: 
Analysis of DI data.
Uses mainly two classes 
- DILineStruct (can contain multiple DI measurements; used for storage, database com and autodif)
- AbsStruct (contains a single measurement, is extended by variation and scalar data, used for calculation)
Calculation returns a data stream with absolute and baseline values for any selected variometer

Systematische Tests:
1.  (11/2013, OK) Laden von Raw-Datem
2.  Laden von alten Raw-Daten
3.  (11/2013, OK) Laden von AutoDIF Daten
4.  (11/2013, OK) Auswertung von gon/deg Daten
5.  (11/2013, OK) Richtigkeit von Gon-Auswertungen: Vergleich mit Juergens Excel
6.  (11/2013, OK) Auswertung ohne Vario und/oder Scalardaten
7.  (11/2013, OK) Systematischer Test - Einfluss der Variometerkorrektur (Korrektur mit basis und nicht basiskorr Variation - sollte identisch sein, korrektur mit unterschiedlichen Varios)
8.  (11/2013, OK) Systematischer Test der Winkelabhaengigkeit (AutoDiff - Bestimme Tagesvariation in Abhaengigkeit von verschiedenen Winkeln)
9.  (11/2013, not necessary: raw data is always available and the file wold not contain any additional info - use database if comments are required) Laden und Speichern von DIListStructs
10. (11/2013, OK) Datenbankspeicherung
11. Create a direct DataBase input formular in php (and magpy-gui?? -> better refer to php there) 
11. (12/2013, not necessary) Laden von mehreren Files gleichzeitig (mit DILineStruct) - not really necessary
12. Basislinien-Stabilitaet (Berechnung der Zuverlaessigkeit der Basislinien-Extrapolation)
13. Write the documentation with citations of the underlying procedures
14. (12/2013, OK) Show Stereoplot
15. Briefly descripe some related bin files

zu 8:
look at bin_angulardependency.py

Related bins:
bin_absolute (analyse DI measurements)
bin_angulardependency (test the influence of variometerorientation several DI measurements during a day (e.g. autodif))
bin_baselinestability (too be written)


Written by Roman Leonhardt 2011/2012/2013
Version 1.0 (from the 23.02.2012)

"""

from stream import *
from transfer import *
from database import *

import dateutil.parser as dparser

MAGPY_SUPPORTED_ABSOLUTES_FORMATS = ['MAGPYABS','MAGPYNEWABS','AUTODIF','UNKNOWN']
ABSKEYLIST = ['time', 'hc', 'vc', 'res', 'f', 'mu', 'md', 'expectedmire', 'varx', 'vary', 'varz', 'varf', 'var1', 'var2']

miredict = {'UA': 290.0, 'MireTower':41.80333,'MireChurch':51.1831,'MireCobenzl':353.698}

class AbsoluteDIStruct(object):
    def __init__(self, time=0, hc=float(nan), vc=float(nan), res=float(nan), f=float(nan), mu=float(nan), md=float(nan), expectedmire=float(nan),varx=float(nan), vary=float(nan), varz=float(nan), varf=float(nan), var1=float(nan), var2=float(nan), temp=float(nan), person='', di_inst='', f_inst=''):
        self.time = time
        self.hc = hc
        self.vc = vc
        self.res = res
        self.f = f
        self.mu = mu
        self.md = md
        self.expectedmire = expectedmire
        self.varx = varx
        self.vary = vary
        self.varz = varz
        self.varf = varf
        self.var1 = var1
        self.var2 = var2
        self.temp = temp
        self.person = person
        self.di_inst = di_inst
        self.f_inst = f_inst

    def __repr__(self):
        return repr((self.time, self.hc, self.vc, self.res, self.f, self.mu, self.md, self.expectedmire, self.varx, self.vary, self.varz, self.varf, self.var1, self.var2))


class DILineStruct(object):
    def __init__(self, ndi, nf=0, time=float(nan), laser=float(nan), hc=float(nan), vc=float(nan), res=float(nan), ftime=float(nan), f=float(nan), opt=float(nan), t=float(nan), scaleflux=float(nan), scaleangle=float(nan), azimuth=float(nan), pier='', person='', di_inst='', f_inst='', fluxgatesensor ='', inputdate=''):
        self.time = ndi*[time]
        self.hc = ndi*[hc]
        self.vc = ndi*[vc]
        self.res = ndi*[res]
        self.opt = ndi*[opt]
        self.laser = ndi*[laser]
        self.ftime = nf*[ftime]
        self.f = nf*[f]
        self.t = t
        self.scaleflux = scaleflux
        self.scaleangle = scaleangle
        self.azimuth = azimuth
        self.person = person
        self.pier = pier
        self.di_inst = di_inst
        self.f_inst = f_inst
        self.fluxgatesensor = fluxgatesensor
        self.inputdate = inputdate

    def __repr__(self):
        return repr((self.time, self.hc, self.vc, self.res, self.laser, self.opt, self.ftime, self.f, self.scaleflux, self.scaleangle, self.t, self.azimuth, self.pier, self.person, self.di_inst, self.f_inst, self.fluxgatesensor, self.inputdate))


    def getAbsDIStruct(self):
	"""
	DEFINITION:
            convert the DILineStruct to the AbsDataStruct used for calculations

        EXAMPLE:
            >>> abslinestruct.getAbsDIStruct()
	"""
        try:
            mu1 = self.hc[0]-((self.hc[0]-self.hc[1])/(self.laser[0]-self.laser[1]))*self.laser[0]
            if isnan(mu1):
                mu1 = self.hc[0] # in case of laser(vc0-vc1) = 0
        except:
            mu1 = self.hc[0] # in case of laser(vc0-vc1) = 0
        try:
            md1 = self.hc[2]-((self.hc[2]-self.hc[3])/(self.laser[2]-self.laser[3]))*self.laser[2]
            if isnan(md1):
                md1 = self.hc[2] # in case of laser(vc0-vc1) = 0
        except:
            md1 = self.hc[2]
        try:
            mu2 = self.hc[12]-((self.hc[12]-self.hc[13])/(self.laser[12]-self.laser[13]))*self.laser[12]
            if isnan(mu2):
                mu2 = self.hc[12] # in case of laser(vc0-vc1) = 0
        except:
            mu2 = self.hc[12]
        try:
            md2 = self.hc[14]-((self.hc[14]-self.hc[15])/(self.laser[14]-self.laser[15]))*self.laser[14]
            if isnan(md2):
                md2 = self.hc[14] # in case of laser(vc0-vc1) = 0
        except:
            md2 = self.hc[14]

        mu = (mu1+mu2)/2
        md = (md1+md2)/2
        stream = AbsoluteData()
        tmplist = []
        sortlist = []

        headers = {}
        headers['pillar'] = self.pier
        if self.inputdate == '':
            headers['analysisdate'] = self.time[0]
        else:
            headers['analysisdate'] = self.inputdate

        # The order needs to be changed according to the file list
        for i, elem in enumerate(self.time):
            if 4 <= i < 12 or 16 <= i < 25:
                row = AbsoluteDIStruct()
                row.time = self.time[i]
                row.hc = self.hc[i] # add the leveling correction
                row.vc = self.vc[i]
                row.res = self.res[i]
                row.mu = mu
                row.md = md
                row.expectedmire = self.azimuth
                row.temp = self.t
                row.person = self.person
                if self.fluxgatesensor == '':
                    row.di_inst = self.di_inst
                else:
                    row.di_inst = self.di_inst +'_'+ self.fluxgatesensor
                row.f_inst = self.f_inst
                tmplist.append(row)

        #print tmplist
            
        # sortlist
        for idx,elem in enumerate(tmplist):
            if idx < 4:
                sortlist.append(elem)
            if idx == 4:
                sortlist.insert(2,elem)
            if idx == 5:
                sortlist.insert(3,elem)
            if idx == 6:
                sortlist.insert(2,elem)
            if idx == 7:
                sortlist.insert(3,elem)
            if 7 < idx <= 9:
                sortlist.append(elem)
            if idx == 10:
                sortlist.insert(8,elem)
            if idx == 11:
                sortlist.insert(9,elem)
            if idx == 12:
                sortlist.insert(8,elem)
            if idx == 13:
                sortlist.insert(9,elem)
            if idx == 14:
                sortlist.insert(8,elem)
            if idx == 15:
                sortlist.insert(9,elem)

        if len(self.time) < 26:
            sortlist.append(tmplist[8])
        else:
            sortlist.append(tmplist[-1])

        for elem in sortlist:
            stream.add(elem)        
        return stream


class AbsoluteData(object):
    """
    Creates a list object from input files /url data
    data is organized in columns

    keys are column identifier:
    key in keys: see ABSKEYLIST

    The following application methods are provided:
    - stream.calcabs(key) -- returns stream (with !var2! filled with aic values)

    Supporting internal methods are:
    - self._calcdec() -- calculates dec
    - self._calcinc() -- calculates inc
    
    """
    def __init__(self, container=None, header=None):
        if container is None:
            container = []
        self.container = container
        if header is None:
            header = {}
        self.header = header

    # ----------------
    # Standard functions and overrides for list like objects
    # ----------------

    def add(self, datlst):
        self.container.append(datlst)

    def __str__(self):
        return str(self.container)

    def __repr__(self):
        return str(self.container)

    def __getitem__(self, index):
        return self.container.__getitem__(index)

    def __len__(self):
        return len(self.container)

    def extend(self,datlst,header):
        self.container.extend(datlst)
        self.header = header

    def sorting(self):
        """
        Sorting data according to time (maybe generalize that to some key)
        """
        liste = sorted(self.container, key=lambda tmp: tmp.time)
        return AbsoluteData(liste, self.header)        

    def _corrangle(self,angle):
        if angle > 360:
            angle = angle - 360.0
        elif angle < 0:
            angle = angle + 360.0
        return angle


    # ----------------
    # internal methods
    # ----------------

    def _get_max(self, key):
        if not key in ABSKEYLIST:
            raise ValueError, "Column key not valid"
        elem = max(self, key=lambda tmp: eval('tmp.'+key))
        return eval('elem.'+key)


    def _get_min(self, key):
        if not key in ABSKEYLIST:
            raise ValueError, "Column key not valid"
        elem = min(self, key=lambda tmp: eval('tmp.'+key))
        return eval('elem.'+key)


    def _get_column(self, key):
        """
        returns an numpy array of selected columns from Stream
        """
        if not key in ABSKEYLIST:
            raise ValueError, "Column key not valid"

        return np.asarray([eval('elem.'+key) for elem in self])

    def _nan_helper(self, y):
        """Helper to handle indices and logical indices of NaNs. Taken from eat (http://stackoverflow.com/questions/6518811/interpolate-nan-values-in-a-numpy-array)

        Input:
            - y, 1d numpy array with possible NaNs
        Output:
            - nans, logical indices of NaNs
            - index, a function, with signature indices= index(logical_indices),
              to convert logical indices of NaNs to 'equivalent' indices
        Example:
            >>> # linear interpolation of NaNs
            >>> nans, x= _nan_helper(y)
            >>> y[nans]= np.interp(x(nans), x(~nans), y[~nans])
        """
        return np.isnan(y), lambda z: z.nonzero()[0]

    def _insert_function_values(self, function,**kwargs):
        """
        DEFINITION:
            Add a function-output to the selected values of the data stream -> e.g. get baseline

        PARAMETERS:
        kwargs:
            - funckeys 		(KEYLIST) (default = 'x','y','z','f') 
            - offset 		(float) provide an offset for keys

        USED BY:

        RETURNS:
 	    stream with function values added

        EXAMPLE:
            >>> abstream._calcdec()
        """

        funckeys = kwargs.get('funckeys')
        offset = kwargs.get('offset')
        if not funckeys:
            funckeys = ['x','y','z','f']
        if not offset:
            offset = 0.0

        for elem in self:
            # check whether time step is in function range
            if function[1] <= elem.time <= function[2]:
                functime = (elem.time-function[1])/(function[2]-function[1])
                for key in funckeys:
                    if not key in KEYLIST[1:15]:
                        raise ValueError, "Column key not valid"
                    fkey = 'f'+key
                    if fkey in function[0]:
                        try:
                            newval = float(function[0][fkey](functime)) + offset
                        except:
                            newval = float('nan')
                        exec('elem.var'+key+' = newval')
                    else:
                        pass
            else:
                pass

        return self

    def variocorr(self, thedate, variostream, absstream, **kwargs):
        """
        This function should not be here .... is absresults a stream??
        Function to perform variometercorrection of an absresult object
        towrads the given datetime using the given variometer stream.
        Returns a new absresult object with new datetime and corrected values
        """
        funckeys = kwargs.get('funckeys')
        offset = kwargs.get('offset')
        if not funckeys:
            funckeys = ['x','y','z','f']
        if not offset:
            offset = 0.0

        # 1 Convert absresult - idff to xyz
        absstream = absstream._convertstream('idf2xyz')

        # 2 Convert datetime to number
        newdate = date2num(absstream._testtime(thedate))

        # 3 Interplolate the variometer data
        function = variostream.interpol(funckeys)

        for elem in absstream:
            # 4 Test whether variostream covers the timerange between the abstream value(s) and the datetime
            if function[1] <= elem.time <= function[2] and function[1] <= newdate <= function[2]:
                valatorgtime = (elem.time-function[1])/(function[2]-function[1])
                valatnewtime = (newdate-function[1])/(function[2]-function[1])
                elem.time = newdate
                for key in funckeys:
                    if not key in KEYLIST[1:15]:
                        raise ValueError, "Column key not valid"
                    fkey = 'f'+key
                    if fkey in function[0]:
                        try:
                            orgval = float(function[0][fkey](valatorgtime))
                            newval = float(function[0][fkey](valatnewtime))
                            diff = orgval - newval
                        except:
                            loggerabs.error("variocorr: error in assigning new values")
                            return
                        exec('elem.'+key+' = elem.'+key+' - diff')
                    else:
                        pass
            else:
                loggerabs.warning("method variocorr: Variometer stream does not cover the projected time range") 
                pass

        # 5 Convert absresult - xyzf to idff 
        absstream = absstream._convertstream('xyz2idf')

        return absstream

    def _calcdec(self, **kwargs):
        """
        DEFINITION:
            Calculates declination values from input.
            Returns results in terms of linestruct 

        PARAMETERS:
        kwargs:
            - annualmeans:	(list of floats) a list providing Observatory specific annual mean values in x,y,z nT (e.g. [20000,1000,43000])
            - xstart:		(float) strength of the north component in nT
            - ystart: 		(float) default 0.0 - strength of the east component in nT
                       - if variometer is hdf oriented then xstart != 0, ystart = 0 
                       - if baselinecorrected data is used (or dIdD) use xstart = 0, ystart = 0 
            - deltaD: 		(float) - default 0.0 - eventual correction factor for declination in degree
            - usestep:		(int) use first, second or both of successive measurements (e.g. autodif requires usestep=2)
            - iterator:		(int) switch of loggerabs (e.g. vario not present) in case of iterative approach
            - scalevalue:	(list of floats) scalevalues for each component (e.g. default = [1,1,1]) 
            - debugmode:	(bool) activate additional debug output

        USED BY:

        RETURNS:
            - line: 		(LineStruct)  containing time, y = dec, typ = 'idff', 
					var1 = s0d, var2 = deH, var3 = epZD, t2 = mirediff,
					str1 = person, str2 = di_inst, str3 = f_inst

        EXAMPLE:
            >>> abstream._calcdec()
        """

        xstart = kwargs.get('xstart')
        ystart = kwargs.get('ystart')
        deltaD = kwargs.get('deltaD')
        usestep = kwargs.get('usestep')
        scalevalue = kwargs.get('scalevalue')
        iterator = kwargs.get('iterator')
        debugmode = kwargs.get('debugmode')
        annualmeans = kwargs.get('annualmeans')

        ang_fac = 1
        if not deltaD:
            deltaD = 0.0
        if not scalevalue:
            scalevalue = [1.0,1.0,1.0]
        if not xstart:
            xstart = 20000.0
        if not ystart:
            ystart = 0.0
        if not annualmeans:
            annualmeans = [20800,1200,43000]
        if not usestep: 
            usestep = 0
        if not iterator:
            iterator = 0
        if not debugmode:
            debugmode = False

        scale_x = scalevalue[0]
        scale_y = scalevalue[1]
        scale_z = scalevalue[2]

        #drop NANs from input stream - positions
        expmire = self._get_column('expectedmire')
        expmire = [float(elem) for elem in expmire]
        expmire = np.mean([elem for elem in expmire if not isnan(elem)])
        poslst = [elem for elem in self if not isnan(elem.hc) and not isnan(elem.vc)]

        try:
            if len(poslst) < 1:
                loggerabs.warning("_calcdec: could not identify measurement positions - aborting")
                return LineStruct()
        except:
            loggerabs.warning("_calcdec: could not assign measurement positions - aborting")
            return LineStruct()

        # Check that: Should be correct if the order of input values is correct
        miremean = np.mean([poslst[1].mu,poslst[1].md]) # fits to mathematica
        # relative mire position of theo is either miremean +90 or -90
        # if sheet is exactly used then it would be easy... however sensor down first measurements have not frequently be used...
        if poslst[1].mu-5 < (miremean-90.0) < poslst[1].mu+5:
            mireval = miremean-90.0
        else:
            mireval = miremean+90.0
        mirediff = self._corrangle(expmire - mireval)

        loggerabs.debug("_calcdec: Miren: %f, %f, %f" % (expmire, poslst[1].mu, miremean))

        # -- Get mean values for x and y
        # ------------------------------
        meanx, meany = 0.0,0.0
        xcol, ycol = [],[]
        for idx, elem in enumerate(poslst):
            if idx < 9:
                if not isnan(elem.varx):
                    xcol.append(elem.varx)
                if not isnan(elem.vary):
                    ycol.append(elem.vary)
        if len(xcol) > 0:
            meanx = np.mean(xcol)
        if len(ycol) > 0:
            meany = np.mean(ycol)
            
        nr_lines = len(poslst)
        dl1,dl2,dl2tmp,variocorr, variohlst = [],[],[],[],[] # temporary lists

        # -- check, whether inclination and declination values are present:
        # ------------------------------
        if nr_lines < 9:
            linecount = nr_lines
        else:
            linecount = (nr_lines-1)/2

        # -- cylce through declinations measurements:
        # ------------------------------
        for k in range(linecount):
            if (poslst[k].hc > poslst[k].vc):
                val = poslst[k].hc-poslst[k].vc
            else:
                val = poslst[k].hc + (360) - poslst[k].vc
            signum = np.sign(np.tan(val))
            # xstart and ystart are already variometercorrected from iteration step 1 on
            variox = (poslst[k].varx-meanx)*scale_x
            varioy = (poslst[k].vary-meany)*scale_y
            if isnan(variox):
                variox = 0.
            if isnan(varioy):
                varioy = 0.
            hstart = np.sqrt((xstart+variox)**2 + (ystart+varioy)**2)
            if hstart == 0:
                rescorr = 0
            else:
                rescorr = signum * np.arcsin( poslst[k].res / hstart )
            if (xstart+poslst[k].varx) == 0:
                variocorr.append(0)
            else:
                variocorr.append(np.arctan((ystart+varioy)/(xstart+variox)))
            dl1.append( poslst[k].hc*np.pi/(180.0) + rescorr - variocorr[k])
            loggerabs.debug("_calcdec: Horizontal angles: %f, %f, %f" % (poslst[k].hc, rescorr, variocorr[k]))

        try:
            if len(dl1) < 8:
                loggerabs.warning("_calcdec: horizontal angles could not be assigned - aborting")
                return LineStruct()
        except:
            loggerabs.warning("_calcdec: horizontal angles could not be assigned - aborting")
            return LineStruct()

        # use selected steps, default is average....
        for k in range(0,7,2):
            if usestep == 1:
                dl2mean = dl1[k]
            elif usestep == 2:
                dl2mean = dl1[k+1]
            else:
                try:
                    dl2mean = np.mean([dl1[k],dl1[k+1]])
                except:
                    loggerabs.error("_calcdec:  %s : Data missing: check whether all fields are filled"% num2date(poslst[0].time).replace(tzinfo=None))
                    pass
            dl2tmp.append(dl2mean)
            loggerabs.debug("_calcdec: Selected Dec: %f" % (dl2mean*180/np.pi))
            if dl2mean < np.pi:
                dl2mean += np.pi/2
            else:
                dl2mean -= np.pi/2
            #dl2tmp.append(dl2mean)
            dl2.append(dl2mean)

        decmean = np.mean(dl2)*180.0/np.pi - 180.0

        loggerabs.debug("_calcdec:  Mean Dec: %f, %f" % (decmean, mirediff))

        #miremean = np.mean([poslst[1].mu,poslst[1].md]) # fits to mathematica
        
        #Initialize HC if no input in this column = 0
        try:
            if (poslst[8].hc == 0 or poslst[8].hc == 180):
                for k in range(8,16):
                    self[k].hc += decmean
        except:
            if iterator == 0:
                loggerabs.warning("_calcdec: %s : No inclination measurements available"% num2date(poslst[0].time).replace(tzinfo=None))
            pass

        # Stupid test of validity - needs to be removed if input order is finally correct
        if 90 > self._corrangle(mirediff + decmean) >= 0:
            corrfac = 0.0
        elif  360 >= self._corrangle(mirediff + decmean) > 270:
            corrfac = 0.0
        else:
            corrfac = 180.0
            mirediff = self._corrangle(mirediff - 180.0)

        if (np.max(dl2)-np.min(dl2))>0.1:
            if iterator == 0:
                loggerabs.error('_calcdec: %s : Check the horizontal input of absolute data (or xstart value)' % num2date(poslst[0].time).replace(tzinfo=None))

        loggerabs.debug("_calcdec:  Dec calc: %f, %f, %f, %f" % (decmean, mirediff, variocorr[0], deltaD))

        dec = self._corrangle(decmean + mirediff + variocorr[0]*180.0/np.pi + deltaD)

        loggerabs.debug("_calcdec:  All (dec: %f, decmean: %f, mirediff: %f, variocorr: %f, delta D: %f and ang_fac: %f, hstart: %f): " % (dec, decmean, mirediff, variocorr[0], deltaD, ang_fac, hstart))

        s0d = (dl2tmp[0]-dl2tmp[1]+dl2tmp[2]-dl2tmp[3])/4*hstart
        deH = (-dl2tmp[0]-dl2tmp[1]+dl2tmp[2]+dl2tmp[3])/4*hstart
        loggerabs.debug("_calcdec:  collimation angle (dl2tmp): %f, %f, %f, %f; hstart: %f" % (dl2tmp[0],dl2tmp[1],dl2tmp[2],dl2tmp[3],hstart))
        if dl2tmp[0]<dl2tmp[1]:
            epZD = (dl2tmp[0]-dl2tmp[1]-dl2tmp[2]+dl2tmp[3]+2*np.pi)/4*hstart
        else:
            epZD = (dl2tmp[0]-dl2tmp[1]-dl2tmp[2]+dl2tmp[3]-2*np.pi)/4*hstart
        
        resultline = LineStruct()
        resultline.time = poslst[0].time
        resultline.y = dec
        resultline.typ = 'idff'         
        resultline.var1 = s0d
        resultline.var2 = deH
        resultline.var3 = epZD
        resultline.t2 = mirediff
        # general info:
        resultline.str1 = poslst[0].person
        resultline.str2 = poslst[0].di_inst
        resultline.str3 = poslst[0].f_inst

        return resultline


    def _calcinc(self, linestruct, **kwargs):
        """
        DEFINITION:
            Calculates inclination values from input.
            Need input of a LineStruct Object containing the results of _calcdec 

        PARAMETERS:
        variable:
            - line		(LineStruct) a line containing results from _calcdec()
        kwargs:
            - annualmeans:	(list of floats) a list providing Observatory specific annual mean values in x,y,z nT (e.g. [20000,1000,43000])
            - incstart		(float) - default 45.0 - inclination value in deg
            - deltaI: 		(float) - default 0.0 - eventual correction factor for inclination in degree
            - usestep:		(int) use first, second or both of successive measurements (e.g. autodif requires usestep=2)
            - iterator:		(int) switch of loggerabs (e.g. vario not present) in case of iterative approach
            - scalevalue:	(list of floats) scalevalues for each component (e.g. default = [1,1,1]) 
            - debugmode:	(bool) activate additional debug output -- !!!!!!! removed and replaced by loggin !!!!!
  
        USED BY:

        REQUIRES:
            a LineStruct element as returned by _calcdec

        RETURNS:
            - line,xstart,ystart: 	(LineStruct, float, float) last two for optimzing calcdec in an iterative process
                                        LineStruct is extended by x = inc, typ = 'idff', z=fstart, f=fstart,
					var4 = s0i, var5 = epzi, dx = basex, dy = basey,
					dz = basez, df = deltaf, t2 = calcscaleval

        EXAMPLE:
            >>> abstream._calcinc()
        """
        
        incstart = kwargs.get('incstart')
        scalevalue = kwargs.get('scalevalue')
        deltaI = kwargs.get('deltaI')
        iterator = kwargs.get('iterator')
        debugmode = kwargs.get('debugmode')
        annualmeans = kwargs.get('annualmeans')
        usestep = kwargs.get('usestep')

        ang_fac = 1
        if not scalevalue:
            scalevalue = [1.0,1.0,1.0]
        if not incstart:
            incstart = 45.0
        if not iterator:
            iterator = 0
        if not debugmode:
            debugmode = False
        if not usestep: 
            usestep = 0

        scale_x = scalevalue[0]
        scale_y = scalevalue[1]
        scale_z = scalevalue[2]

        # Initialize variometer and scalar instruments .... maybe better not here
        variotype = 'None'
        scalartype = 'None'

        # -- Get the variometer and scalar means from then absolute file
        # --------------------------------------------------------------
        #drop NANs from input stream - positions and get means
        poslst = [elem for elem in self if not isnan(elem.hc) and not isnan(elem.vc)]
        fcol = self._get_column('f')
        mflst = [elem for elem in fcol if not isnan(elem)]
        fvcol = self._get_column('varf')
        mfvlst = [elem for elem in fvcol if not isnan(elem)]
        # Select variometer readings for existing intensity data
        variox, varioy, varioz, flist, fvlist, dflist  = [],[],[],[],[],[]
        foundfirstelem = 0
        for elem in self:
            if len(mflst) > 0 and not isnan(elem.f):
                flist.append(elem.f)
                if not isnan(elem.varz) and not isnan(elem.vary) and not isnan(elem.varx):
                    variox.append(scale_x*elem.varx) 
                    varioy.append(scale_y*elem.vary) 
                    varioz.append(scale_z*elem.varz)
                if not isnan(elem.varf):
                    fvlist.append(elem.varf)
                    dflist.append(elem.f-elem.varf)
            elif len(mflst) == 0 and len(mfvlst) > 0:
                if not isnan(elem.varz) and not isnan(elem.vary) and not isnan(elem.varx):
                    variox.append(scale_x*elem.varx) 
                    varioy.append(scale_y*elem.vary) 
                    varioz.append(scale_z*elem.varz)
                if not isnan(elem.varf):
                    fvlist.append(elem.varf)
                    if foundfirstelem == 0:
                        if iterator == 0:
                            loggerabs.debug("_calcinc: %s : no f in absolute file -- using scalar values from specified scalarpath" % (num2date(self[0].time).replace(tzinfo=None)))
                        foundfirstelem = 1

        if len(mflst)>0:
            meanf = np.mean(flist)
            loggerabs.debug("_calcinc: Using F from Absolute files") 
        elif len(mfvlst)>0:
            meanf = np.mean(fvlist)
            loggerabs.debug("_calcinc: Using F from provided scalar path") 
        else:
            #meanf = 0.
            meanf = (annualmeans[0]*annualmeans[0] + annualmeans[1]*annualmeans[1] + annualmeans[2]*annualmeans[2])
            #return emptyline, 20000.0, 0.0

        

        if len(variox) == 0:
            if iterator == 0:
                loggerabs.warning("_calcinc: %s : no variometervalues found" % num2date(self[0].time).replace(tzinfo=None))
            # set means to zero...
            meanvariox = 0.0
            meanvarioy = 0.0
            meanvarioz = 0.0
        else:
            meanvariox = np.mean(variox)
            meanvarioy = np.mean(varioy)
            meanvarioz = np.mean(varioz)

        xcorr =  meanf * np.cos( incstart *np.pi/(180.0) ) * np.cos ( linestruct.y *np.pi/(180.0) ) - meanvariox
        ycorr =  meanf * np.cos( incstart *np.pi/(180.0) ) * np.sin ( linestruct.y *np.pi/(180.0) ) - meanvarioy
        zcorr =  meanf * np.sin( incstart *np.pi/(180.0) ) - meanvarioz

        #drop NANs from input stream - fvalues
        if len(dflist) > 0:
            deltaF = np.mean(dflist)
        else:
            deltaF = float(nan)

        # -- Start with the inclination calculation
        # --------------------------------------------------------------
        nr_lines = len(poslst)
        I0Diff1,I0Diff2,xDiff1,zDiff1,xDiff2,zDiff2= 0,0,0,0,0,0
        I0list, ppmval,testlst = [],[],[]
        cnt = 0
        mirediff = linestruct.t2

        # Check that mirediff is correct
        # get the correct hc values and replace 0 and 180 degree with the correct data
        #print "Hc = ", linestruct.y - mirediff
        #print linestruct.y, mirediff

        # If only D measurements are available then no suitable estimate of H can be obtained
        # Therefore we use an arbitrary start value -- Testing of the validity of this approach needs to be conducted
        if nr_lines < 16: # only declination measurements available so far
            return linestruct, 20000.0, 0.0
        
        # - Now cycle through inclination steps and apply residuum correction
        for k in range((nr_lines-1)/2,nr_lines):
            val = poslst[k].vc
            try:
                xtmp = (scale_x*poslst[k].varx) + xcorr
                ytmp = (scale_y*poslst[k].vary) + ycorr
                ztmp = (scale_z*poslst[k].varz) + zcorr
                ppmtmp = np.sqrt(xtmp**2 + ytmp**2 + ztmp**2)
                if isnan(ppmtmp):
                    ppmval.append(meanf)
                else:
                    ppmval.append(ppmtmp)
            except:
                ppmval.append(meanf)
            if not ppmval[cnt] == 0:
                rcorri = np.arcsin(poslst[k].res/ppmval[cnt])
            else:
                rcorri = 0.0
            #if poslst[k].hc < 0:
            #    poslst[k].hc = poslst[k].hc + 360*ang_fac
            if poslst[k].vc > (poslst[k].hc + mirediff):
                quad = poslst[k].vc - (poslst[k].hc + mirediff)
            else:
                quad = poslst[k].vc + 360.0 - (poslst[k].hc + mirediff)
            # The signums are essential for the collimation angle calculation
            # ToDo: check regarding correctness for different location/angles 
            # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 
            #signum1 = np.sign(np.tan(quad*np.pi/180))
            signum1 = np.sign(-np.cos(quad*np.pi/180.0))
            signum2 = np.sign(np.sin(quad*np.pi/180.0))
            if signum2>0:
                PiVal=2*np.pi
            else:
                PiVal=np.pi
            I0 = (signum1*poslst[k].vc*np.pi/180.0 - signum2*rcorri - signum1*PiVal)

            #print signum1, poslst[k].vc, quad, I0, rcorri, signum2, PiVal
            # check the quadrant
            if I0 > np.pi:
                I0 = 2*np.pi-I0
            elif I0 < -np.pi:
                I0 += 2*np.pi
            elif  I0 < 0:
                I0 = -I0
                
            if k < nr_lines-1:
                I0list.append(I0)       
                I0Diff1 += signum2*I0
                xDiff1 += signum2*poslst[k].varx
                zDiff1 += signum2*poslst[k].varz
                I0Diff2+= signum1*I0
                xDiff2 += signum1*poslst[k].varx
                zDiff2 += signum1*poslst[k].varz
            else:
                scaleangle = poslst[k].vc
                minimum = 10000
                calcscaleval = 999.0
                for n in range((nr_lines-1)/2,nr_lines-1):
                    rotation = np.abs(scaleangle - poslst[n].vc)
                    if 0.03 < rotation < 0.5: # Only analyze scale value if last step (17) deviates between 0.03 and 0.5 degrees from any other inclination value 
                        fieldchange = (-np.sin(np.mean(I0list))*(poslst[n].varx-poslst[k].varx)/ppmval[cnt] + np.cos(np.mean(I0list))*(poslst[n].vary-poslst[k].vary)/ppmval[cnt])*180/np.pi 
                        deltaB = rotation+fieldchange
                        deltaR = np.abs(poslst[n].res-poslst[k].res)
                        minimum = rotation
                        if (deltaR == 0):
                            calcscaleval = 999.0
                        else:
                            calcscaleval = ppmval[cnt] * deltaB/deltaR * np.pi/180
                        loggerabs.debug("_calcinc: Scalevalue calculation in calcinc - Fieldchange: %f, Scalevalue: %f, DeltaR: %f" % (fieldchange,calcscaleval,deltaR))
   
            cnt += 1

        i1list,i1tmp = [],[]

        for k in range(0,7,2):
            if usestep == 1:
                i1mean = I0list[k]
            elif usestep == 2:
                i1mean = I0list[k+1]
            else:
                i1mean = np.mean([I0list[k],I0list[k+1]])
            i1tmp.append(i1mean)
            i1list.append(i1mean)


        I0Diff1 = I0Diff1/2.
        xDiff1 = xDiff1/2.
        zDiff1 = zDiff1/2.
        I0Diff2 = I0Diff2/2.
        xDiff2 = xDiff2/2.
        zDiff2 = zDiff2/2.

        # Variometer correction to start time is missing for f value and inc ???
        inc = np.mean(i1list)*180.0/np.pi + deltaI

        if isnan(inc): # if only dec measurements are available
            inc = 0.0
        # Dec is already variometer corrected (if possible) and transferred to time[0]
        tmpH = meanf * np.cos( inc *np.pi/(180.0) )
        tmpZ = meanf * np.sin( inc *np.pi/(180.0) )
        # check for inclination error in file inc
        #   -- the following part may cause problems in case of close to polar positions and locations were X is larger than Y
        if (90-inc) < 0.1:
            loggerabs.error('_calcinc: %s : Inclination warning... check your vertical measurements. inc = %f, mean F = %f' % (num2date(self[0].time).replace(tzinfo=None), inc, meanf))
            #loggerabs.error(I0list)
            h_adder = 0.
        else:
            h_adder = np.sqrt(tmpH**2 - meanvarioy**2) - meanvariox

        if not isnan(poslst[0].varx):
            hstart = np.sqrt((scale_x*poslst[0].varx + h_adder)**2 + (scale_y*poslst[0].vary)**2)
            xstart = hstart * np.cos ( linestruct.y *np.pi/(180.0) )
            ystart = hstart * np.sin ( linestruct.y *np.pi/(180.0) )
            zstart = scale_z*poslst[0].varz + tmpZ - meanvarioz
            fstart = np.sqrt(xstart**2 + ystart**2 + zstart**2)
        else:
            variotype = 'None'
            hstart = tmpH
            zstart = tmpZ
            xstart = hstart # use dec to calc correctly
            ystart = 0.0
            fstart = np.sqrt(xstart**2 + ystart**2 + zstart**2)
            xDiff1 = 0.0
            zDiff1 = 0.0
            xDiff2 = 0.0
            zDiff2 = 0.0

        if not meanf == 0:
            inc = np.arctan(zstart/hstart)*180.0/np.pi
            # Divided by 4 - need to be corrected if scalevals are used - don't thing so (leon, June 2012)
            s0i = -I0Diff1/4*fstart - xDiff1*np.sin(inc*np.pi/180) - zDiff1*np.cos(inc*np.pi/180) 
            epzi = (-I0Diff2/4 - (xDiff2*np.sin(inc*np.pi/180) - zDiff2*np.cos(inc*np.pi/180))/(4*fstart))*zstart;
        else:
            loggerabs.warning("_calcinc: %s : no intensity measurement available - presently using an x value of 20000 nT for Dec"  % num2date(self[0].time).replace(tzinfo=None))
            fstart, deltaF, s0i, epzi = float(nan),float(nan),float(nan),float(nan)
            xstart = 20000 ## arbitrary
            ystart = 0.0

        # Baselinevalues:
        basex = xstart - scale_x*poslst[0].varx
        basey = ystart - scale_y*poslst[0].vary
        basez = zstart - scale_z*poslst[0].varz

        # Putting data to linestruct:
        linestruct.x = inc
        linestruct.z = fstart
        linestruct.f = fstart #np.array([basex,basey,basez])
        linestruct.dx = basex
        linestruct.dy = basey
        linestruct.dz = basez
        linestruct.df = deltaF
        linestruct.typ = 'idff'         
        linestruct.t2 = calcscaleval
        linestruct.var4 = s0i  # replaces Mirediff from _calcdec
        linestruct.var5 = epzi

        return linestruct, xstart, ystart

    def calcabsolutes(self, debugmode=None, **kwargs):
        """
        DEFINITION:
            Calculates DI values by calling calcdec and calcinc methods.
            Uses an iterative approach of dec and inc calculation.
            Provide variometer and scalar values for optimal results.
            If no variometervalues are provided then only dec and inc are calculated correctly

        PARAMETERS:
        variable:
            - line		(LineStruct) a line containing results from _calcdec()
        kwargs:
            - annualmeans:	(list of floats) a list providing Observatory specific annual mean values in x,y,z nT (e.g. [20000,1000,43000])
            - incstart		(float) - default 45.0 - inclination value in deg
            - deltaI: 		(float) - default 0.0 - eventual correction factor for inclination in degree
            - usestep:		(int) use first, second or both of successive measurements (e.g. autodif requires usestep=2)
            - iterator:		(int) switch of loggerabs (e.g. vario not present) in case of iterative approach
            - scalevalue:	(list of floats) scalevalues for each component (e.g. default = [1,1,1]) 
            - debugmode:	(bool) activate additional debug output -- !!!!!!! removed and replaced by loggin !!!!!
            - printresults      (bool) - if True print results to screen
  
        USED BY:

        REQUIRES:

        RETURNS:

        EXAMPLE:
            >>> stream.calcabsolutes(usestep=2,annualmeans=[20000,1200,43000],printresults=True)

        APPLICATION:
            absst = absRead(path_or_url=abspath,azimuth=azimuth,output='DIListStruct')
            stream = elem.getAbsDIStruct()
            variostr = read(variopath)
            variostr =variostr.rotation(alpha=varioorientation_alpha, beta=varioorientation_beta)
            vafunc = variostr.interpol(['x','y','z'])
            stream = stream._insert_function_values(vafunc)
            scalarstr = read(scalarpath)
            scfunc = scalarstr.interpol(['f'])
            stream = stream._insert_function_values(scfunc,funckeys=['f'],offset=deltaF)
            result = stream.calcabsolutes(usestep=2,annualmeans=[20000,1200,43000],printresults=True)
        """

        #plog = PyMagLog()
        incstart = kwargs.get('incstart')
        scalevalue = kwargs.get('scalevalue')
        annualmeans = kwargs.get('annualmeans')
        unit = kwargs.get('unit')
        xstart = kwargs.get('xstart')
        ystart = kwargs.get('ystart')
        deltaD = kwargs.get('deltaD')
        deltaI = kwargs.get('deltaI')
        usestep = kwargs.get('usestep')
        printresults = kwargs.get('printresults')

        if not deltaI:
            deltaI = 0.0
        if not deltaD:
            deltaD = 0.0
        if not scalevalue:
            scalevalue = [1.0,1.0,1.0]
        if not usestep: 
            usestep = 0
        if not annualmeans:
            annualmeans = [20800,1200,43500]
        if not xstart:
            xstart = annualmeans[0]
        if not ystart:
            xstart = annualmeans[1]
        if not incstart:
            incstart = 180/np.pi * np.arctan(annualmeans[2] / np.sqrt(annualmeans[0]*annualmeans[0] + annualmeans[1]*annualmeans[1]))

        for i in range(0,3):
            # Calculate declination value (use xstart and ystart as boundary conditions
            resultline = self._calcdec(xstart=xstart,ystart=ystart,deltaD=deltaD,usestep=usestep,scalevalue=scalevalue,iterator=i,annualmeans=annualmeans,debugmode=debugmode)
            # Calculate inclination value
            if debugmode:
                print "Calculated D (%f) - iteration step %d" % (resultline[2],i)
                print "All results: " , resultline
            # requires succesful declination determination
            if isnan(resultline.y):
                try:
                    loggerabs.error('%s : CalcAbsolutes: Declination could not be determined - aborting' % num2date(self[0].time).replace(tzinfo=None))
                except:
                    loggerabs.error('unkown : CalcAbsolutes: Declination could not be determined - aborting')
                break
            # use incstart and ystart as boundary conditions
            try: # check, whether outline already exists
                if isnan(outline.x):
                    inc = incstart
                else:
                    inc = outline.x
            except:
                inc = incstart
            outline, xstart, ystart = self._calcinc(resultline,scalevalue=scalevalue,incstart=inc,deltaI=deltaI,iterator=i,usestep=usestep,annualmeans=annualmeans)
            
            if debugmode:
                print "Calculated I (%f) - iteration step %d" %(outline[1],i)


        #test whether outline is a linestruct object - if not use an empty object
        try:
            test = outline.x

            loggerabs.info('%s : Declination: %s, Inclination: %s, H: %.1f, F: %.1f' % (num2date(outline.time), deg2degminsec(outline.y),deg2degminsec(outline.x),outline.f*np.cos(outline.x*np.pi/180),outline.f))

            if printresults:
                print 'Vector:'
                print 'Declination: %s, Inclination: %s, H: %.1f, F: %.1f' % (deg2degminsec(outline.y),deg2degminsec(outline.x),outline.f*np.cos(outline.x*np.pi/180),outline.f)
                print 'Collimation and Offset:'
                print 'Declination:    S0: %.3f, delta H: %.3f, epsilon Z: %.3f\nInclination:    S0: %.3f, epsilon Z: %.3f\nScalevalue: %.3f' % (outline.var1,outline.var2,outline.var3,outline.var4,outline.var5,outline.t2)

        except:
            text = 'calcabsolutes: invalid LineStruct Object returned from calcinc function'
            loggerabs.warning(text)
            if printresults:
                print text
            outline = LineStruct()

        return outline

#
#  Now import the format libraries
#

from lib.magpy_absformats import *


def _logfile_len(fname, logfilter):
    f = open(fname,"rb")
    cnt = 0
    for line in f:
        if logfilter in line:
            cnt = cnt +1
    return cnt
 

def deg2degminsec(value):
    """
    Function to convert deg.decimals to a string with deg min and seconds.decimals
    """
    if value > 360:
        return 'larger than 360'

    if isnan(value):
        return 'nan'

    degree = int(value)
    tminutes = np.abs(value - int(value))*60
    minutes = int(tminutes)
    tseconds = (tminutes-minutes)*60
    seconds = int(np.round(tseconds))
    if seconds == 60:
        minutes = minutes+1
        seconds = 0
    if minutes == 60:
        if degree < 0:
            degree = degree - 1
        else:
            degree = degree + 1
        minutes = 0

    return str(degree)+":"+str(minutes)+":"+str(seconds)
    

def absRead(path_or_url=None, dataformat=None, headonly=False, **kwargs):
    """
    optional keywords:
    username: for authentication in ftp and ssh access
    password: for authentication (following the example of http://www.voidspace.org.uk/python/articles/authentication.shtml
    """
    # Not used so far - maybe for simplifying ftp or ssh
    username = kwargs.get('username')
    password = kwargs.get('password')
    archivepath = kwargs.get('archivepath')
    output = kwargs.get('output')

    # -- No path
    if not path_or_url:
        messagecont = "File not specified"
        return [],messagecont
    # -- Create Data Container
    stream = AbsoluteData()
    # -- Check file
    if not isinstance(path_or_url, basestring):
        # not a string - we assume a file-like object
        pass
    elif "://" in path_or_url:
        # some URL
        #proxy_handler = urllib2.ProxyHandler( {'http': '138.22.156.44:8080', 'https' : '138.22.156.44:443', 'ftp' : '138.22.156.44:8021' } )           
        #opener = urllib2.build_opener(proxy_handler,urllib2.HTTPBasicAuthHandler(),urllib2.HTTPHandler, urllib2.HTTPSHandler,urllib2.FTPHandler)
        # install this opener
        #urllib2.install_opener(opener)       
  
        # extract extension if any
        suffix = '.'+os.path.basename(path_or_url).partition('.')[2] or '.tmp'
        name = os.path.basename(path_or_url).partition('.')[0] # append the full filename to the temporary file
        fh = NamedTemporaryFile(suffix=name+suffix,delete=False)
        fh.write(urllib2.urlopen(path_or_url).read())
        fh.close()
        stream = _absRead(fh.name, dataformat, headonly, **kwargs)
        os.remove(fh.name)
    else:
        # some file name
        pathname = path_or_url
        stream = _absRead(pathname, dataformat, headonly, **kwargs)
        if len(stream) == 0:
            # try to give more specific information why the stream is empty
            if has_magic(pathname) and not glob(pathname):
                raise Exception("No file matching file pattern: %s" % pathname)
            elif not has_magic(pathname) and not os.path.isfile(pathname):
                raise IOError(2, "No such file or directory", pathname)
            # Only raise error if no starttime/endtime has been set. This
            # will return an empty stream if the user chose a time window with
            # no data in it.
            # XXX: Might cause problems if the data is faulty and the user
            # set starttime/endtime. Not sure what to do in this case.
            #elif not 'starttime' in kwargs and not 'endtime' in kwargs:
            #    raise Exception("Cannot open file/files: %s" % pathname)

    return stream

def _absRead(filename, dataformat=None, headonly=False, **kwargs):
    """
    Reads a single file into a ObsPy Stream object.
    """

    output = kwargs.get('output')
    # get format type
    format_type = None
    if not dataformat:
        # auto detect format - go through all known formats in given sort order
        for format_type in MAGPY_SUPPORTED_ABSOLUTES_FORMATS:
            # check format
            if isAbsFormat(filename, format_type):
                break
    else:
        # format given via argument
        dataformat = dataformat.upper()
        try:
            formats = [el for el in MAGPY_SUPPORTED_ABSOLUTES_FORMATS if el == dataformat]
            format_type = formats[0]
        except IndexError:
            msg = "Format \"%s\" is not supported. Supported types: %s"
            raise TypeError(msg % (dataformat, ', '.join(MAGPY_SUPPORTED_ABSOLUTES_FORMATS)))
    # file format should be known by now
    print format_type

    stream = readAbsFormat(filename, format_type, headonly=headonly, **kwargs)

    # If stream could not be read return an empty datastream object
    try:
        xxx = len(stream)
    except:
        stream = DataStream()

    return stream


def analyzeAbsFiles(debugmode=None,**kwargs):
    """
    Analyze absolute files from a specific path
    Requires an analysis directory for treatment of downloaded absolute files.
    By default flagged data is removed. In order to keep them for analysis use the useflagged=True keyword
    Optional keywords:
    useflagged (boolean) -- default False
    archivepath -- archive directory to which tsuccessfully analyzed data is moved to
    access_ftp -- retrives data from an ftp directory first and removes them after successful analysis
    printresults (boolean) -- screen output of calculation results
    disableproxy (boolean) -- by default system settings are used        
    -- calcabs calculation parameters:
            usestep: (int) for selecting whether first (1), second (2) or a mean (0) of both repeated measurements at each "Lage" is used 
    """

    plog = PyMagLog()
    
    path_or_url = kwargs.get('path_or_url')
    variopath = kwargs.get('variopath')
    scalarpath = kwargs.get('scalarpath')
    deltaF = kwargs.get('deltaF')
    printresults = kwargs.get('printresults')
    # Parameters for absolute calculation (used in calcabs -> und subfunctions _calcdev, _calcinc
    incstart = kwargs.get('incstart')
    scalevalue = kwargs.get('scalevalue')
    unit = kwargs.get('unit')
    xstart = kwargs.get('xstart')
    ystart = kwargs.get('ystart')
    deltaD = kwargs.get('deltaD')
    deltaI = kwargs.get('deltaI')
    alpha = kwargs.get('alpha')
    beta = kwargs.get('beta')
    useflagged = kwargs.get('useflagged')
    usestep = kwargs.get('usestep')
    outputformat  = kwargs.get('outputformat')
    summaryfile = kwargs.get('summaryfile')
    analysispath = kwargs.get('analysispath')
    archivepath = kwargs.get('archivepath')
    absidentifier = kwargs.get('absidentifier') # Part of filename, which defines absolute files
    # Timerange
    starttime = kwargs.get('starttime')
    endtime = kwargs.get('endtime')
    # Not used so far are username and passwd
    username = kwargs.get('username')
    password = kwargs.get('password')
    disableproxy = kwargs.get('disableproxy')
    
    if not absidentifier:
        absidentifier = 'AbsoluteMeas.txt'
    if not deltaF:
        deltaF = 0.0
    if not deltaI:
        deltaI = 0.0
    if not deltaD:
        deltaD = 0.0
    if not scalevalue:
        scalevalue = [1.0,1.0,1.0]
    if not unit:
        unit = 'deg'
    if unit=='gon':
        ang_fac = 400./360.
    elif unit == 'rad':
        ang_fac = np.pi/180.
    else:
        ang_fac = 1
    if not incstart:
        incstart = 45.0
    if not xstart:
        xstart = 20000.0
    if not ystart:
        ystart = 0.0
    if not usestep: 
        usestep = 0
    if not outputformat: # accepts idf, hdz and xyz
        outputformat = 'xyz'
    if username: # Needs to be checked: Using username and passwd within url instead
        passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passman.add_password(None, path_or_url, username, password)
        authhandler = urllib2.HTTPBasicAuthHandler(passman)
        opener = urllib2.build_opener(authhandler)
        urllib2.install_opener(opener)
    if disableproxy:
        proxy_handler = urllib2.ProxyHandler( {} )           
        opener = urllib2.build_opener(proxy_handler)
        # install this opener
        urllib2.install_opener(opener)

    localfilelist = []
    st = DataStream()
    varioinst = '-'
    scalarinst = '-'

    loggerabs.info('--- Start absolute analysis at %s ' % str(datetime.now()))
    print "Using unit with angfac", unit, ang_fac

    # now check the contents of the analysis path - url part is yet missing
    if not os.path.isfile(path_or_url):
        if os.path.exists(path_or_url):
            for infile in iglob(os.path.join(path_or_url,'*'+absidentifier)):
                localfilelist.append(infile)
        elif  "://" in path_or_url: # URL part
            # get all files in URL path
            # (changes from 04.09)
            req = urllib2.Request(path_or_url)
            try:
                response = urllib2.urlopen(req)
            except urllib2.URLError, e:
                if hasattr(e, 'reason'):
                    loggerabs.error('URLLIB2 Failed to reach a server. Reason: %s' % e.reason)
                elif hasattr(e, 'code'):
                    loggerabs.error('The server couldn\'t fulfill the request. Error code: %s' % e.code)
                return

            path = response.geturl()
            html_string = response.read()

            # Distinguish between directory and file - get filename and add to path -> add to list
            datlst = html_string.split("\n")
            firstline = datlst[0].split()
            if datlst[0].startswith('# MagPy Absolutes') or datlst[1].startswith('Miren:'):
                # found single file
                localfilelist.append(path)
                pass
            elif len(datlst[0].split()) > 8: 
                for elem in datlst:
                    try:
                        absfile = elem.split()[-1]
                        if absfile.endswith(absidentifier):
                            localfilelist.append(path+absfile)
                    except:
                        pass
            else:
                loggerabs.error('--- -- Aborting AbsAnalysis: no apropriate file found')              
        else:
            loggerabs.error('--- -- Aborting AbsAnalysis: could not identify path_or_url')
            return  
    else:
        localfilelist.append(path_or_url)

    # Escape for single files:
    assert type(localfilelist)==list

    if len(localfilelist) < 1:
        loggerabs.info('--- -- Aborting AbsAnalysis: no data available')
        print "Aborting AbsAnalysis: no data available"
        return
    
    # if time range is given then limit the localfilelist
    elem = localfilelist[0].split('/')
    splitter = '/'
    try:
        elem = elem.split('\\')
        splitter = '\\'
        loggerabs.info('--- -- AbsAnalysis: Windows type path found')
    except:
        loggerabs.info('--- -- AbsAnalysis: Linux type path found')
    if starttime:
        localfilelist = [elem for elem in localfilelist if (datetime.strptime(elem.split(splitter)[-1][:10],"%Y-%m-%d") >= st._testtime(starttime))]

    if endtime:
        localfilelist = [elem for elem in localfilelist if (datetime.strptime(elem.split(splitter)[-1][:10],"%Y-%m-%d") <= st._testtime(endtime))]
        
    if len(localfilelist) > 0:
        loggerabs.info('--- -- AbsAnalysis: %d DI measurements to be analyzed' % len(localfilelist))
    else:
        loggerabs.error('--- -- Aborting AbsAnalysis: check time range or data source: no DI data present')
        return
 
    # get files from localfilelist and analyze them (localfilelist is not sorted!)
    cnt = 0

    # firstly load all absolutes and get min and max time
    # load vario and scalar data between min and max
    # then do the analysis
    loggerabs.info('AbsAnalysis: Getting time range')
    mintime = 9999999999.0
    maxtime = 0.0
    abst = []
    print 'Getting time range', datetime.utcnow()
    for fi in localfilelist:
        abstr = absRead(path_or_url=fi,archivepath=archivepath)
        if len(abstr) > 0:
            mint = abstr._get_min('time')
            maxt = abstr._get_max('time')
            if mint < mintime:
                mintime = mint
            if maxt > maxtime:
                maxtime = maxt
            abst.append(abstr)

    print 'Min Time', num2date(mintime)
    print 'Max Time', num2date(maxtime)

    # Test of iterative procedure with variable length  (chnage days=30) 
    iterationtime = date2num(num2date(mintime).replace(tzinfo=None)+timedelta(days=30))
    start = mintime
    while start < maxtime:
        print "Do 30 days of analysis between start and iterationtime: starting at ", num2date(start)
        # 1.) Get vario
        print 'Reading varios', datetime.utcnow()
        if variopath:
            variost = read(path_or_url=variopath,starttime=start-0.04,endtime=iterationtime+0.04)
            print "Reading from ", num2date(start), num2date(iterationtime), len(variost)
            variost.header.clear()
            if not useflagged:
                variost = variost.remove_flagged()
            # Provide reorientation angles in case of non-geographically oriented systems: simple case HDZ -> use alpha = dec (at time of sensor setup)
            variost = variost.rotation(alpha=alpha,beta=beta,unit=unit)
            if len(variost) > 0:
                vafunc = variost.interpol(['x','y','z'])

        # 2.) Get scalars
        print 'Reading scalars', datetime.utcnow()
        if scalarpath:
            # scalar instrument and dF are then required
            scalarst = read(path_or_url=scalarpath,starttime=start-0.04,endtime=iterationtime+0.04)
            scalarst.header.clear()
            if not useflagged:
                scalarst = scalarst.remove_flagged()
            if len(scalarst) > 0:
                scfunc = scalarst.interpol(['f'])

        # 3.) Analyse streams
        testlst = [elem for elem in abst if elem._get_min('time') >= start and elem._get_max('time') < iterationtime]
        start = iterationtime
        iterationtime = date2num(num2date(iterationtime).replace(tzinfo=None)+timedelta(days=30))    
        for stream in testlst:
            #print len(stream)
            lengthoferrorsbefore = _logfile_len(logfile,'ERROR')

            # XXX ###################################
            # XXX   Remove the reference to plog !!!
            # XXX ###################################
            cnt += 1
            plog.addcount(cnt, len(localfilelist))
            # ######## Process counter
            print plog.proc_count, " percent"
            # ######## Process counter
            
            # initialize the move function for each fi
            if not archivepath:
                movetoarchive = False
            else:
                movetoarchive = True # this variable will be set false in case of warnings
            loggerabs.info('%s : Analyzing absolute file of length %d' % (fi,len(stream)))
            if len(stream) > 0:
                mint = stream._get_min('time')
                maxt = stream._get_max('time')
                # -- Obtain variometer record and f record for the selected time (1 hour more before and after)
                if variopath:
                    if len(variost) > 0:
                        stream = stream._insert_function_values(vafunc)
                        varioinst = os.path.split(variopath)[0]
                    else:
                        loggerabs.warning('%s : No variometer correction possible' % fi) 
                # Now check for f values in file
                fcol = stream._get_column('f')
                if not len(fcol) > 0 and not scalarpath:
                    movetoarchive = False
                    loggerabs.error('%s : f values are required for analysis -- aborting' % fi)
                    break
                if scalarpath:
                    if len(scalarst) > 0:
                        stream = stream._insert_function_values(scfunc, funckeys=['f'],offset=deltaF)
                        scalarinst = os.path.split(scalarpath)[0]
                    else:
                        loggerabs.warning('%s : Did not find independent scalar values' % fi)
                        
                # use DataStream and its LineStruct to store results
                #print unit
                result = stream.calcabsolutes(incstart=incstart,xstart=xstart,ystart=ystart,unit=unit,scalevalue=scalevalue,deltaD=deltaD,deltaI=deltaI,usestep=usestep,printresults=printresults,debugmode=debugmode)
                result.str4 = varioinst
                if (result.str3 == '-' or result.str3 == '') and not scalarinst == '-':
                    result.str3 = scalarinst

                # Get the amount of error messages after the analysis
                lengthoferrorsafter = _logfile_len(logfile,'ERROR')

                if lengthoferrorsafter > lengthoferrorsbefore:
                    movetoarchive = False
                    
                # check for presence of result in summary-file and append / replace existing data (if more non-NAN values are present)
                nonnan_result, nonnan_line = [],[]
                for key in KEYLIST:
                    try:
                        if not isnan(eval('result.'+key)):
                            nonnan_result.append(eval('result.'+key))
                    except:
                        pass
                newst = DataStream()

                # Create header keys and attributes
                line = LineStruct()
                st.header['col-time'] = 'Epoch'
                st.header['col-x'] = 'i'
                st.header['unit-col-x'] = unit
                st.header['col-y'] = 'd'
                st.header['unit-col-y'] = unit
                st.header['col-z'] = 'f'
                st.header['unit-col-z'] = 'nT'
                st.header['col-f'] = 'f'
                st.header['col-dx'] = 'basex'
                st.header['col-dy'] = 'basey'
                st.header['col-dz'] = 'basez'
                st.header['col-df'] = 'dF'
                st.header['col-t1'] = 'T'
                st.header['col-t2'] = 'ScaleValueDI'
                st.header['col-var1'] = 'Dec_S0'
                st.header['col-var2'] = 'Dec_deltaH'
                st.header['col-var3'] = 'Dec_epsilonZ'
                st.header['col-var4'] = 'Inc_S0'
                st.header['col-var5'] = 'Inc_epsilonZ'
                st.header['col-str1'] = 'Person'
                st.header['col-str2'] = 'DI-Inst'
                st.header['col-str3'] = 'F-Inst'
                st.header['col-str4'] = 'Vario-Inst'

                if outputformat == 'xyz':
                    #for elem in st:
                    result = result.idf2xyz(unit=unit)
                    result.typ = 'xyzf'         
                    st.header['col-x'] = 'x'
                    st.header['unit-col-x'] = 'nT'
                    st.header['col-y'] = 'y'
                    st.header['unit-col-y'] = 'nT'
                    st.header['col-z'] = 'z'
                    st.header['unit-col-z'] = 'nT'
                elif outputformat == 'hdz':
                    #for elem in st:
                    result = result.idf2xyz(unit=unit)
                    #for elem in st:
                    result = result.xyz2hdz(unit=unit)
                    result.typ = 'hdzf'         
                    st.header['col-x'] = 'h'
                    st.header['unit-col-x'] = 'nT'
                    st.header['col-y'] = 'd'
                    st.header['unit-col-y'] = unit
                    st.header['col-z'] = 'z'
                    st.header['unit-col-z'] = 'nT'

                # only write results if no warnings were issued:
                #if movetoarchive:
                if not lengthoferrorsafter > lengthoferrorsbefore:
                    newst.add(result)
                    st.extend(newst, st.header)
            else: # len(stream) <= 0
                movetoarchive = False
                loggerabs.error('%s: File or data format problem - please check' % fi)

            # Get the list index of stream and select the appropriate filename for storage
            if movetoarchive:
                # Get the list index of stream and select the appropriate filename for storage
                index = abst.index(stream)
                fi = localfilelist[index]
                if not "://" in fi: 
                    src = fi
                    fname = os.path.split(src)[1]
                    dst = os.path.join(archivepath,fname)
                    shutil.move(src,dst)
                else:
                    fname = fi.split('/')[-1]
                    suffix = fname.split('.')[-1]
                    passwdtyp = fi.split(':')
                    typus = passwdtyp[0]
                    port = 21
                    passwd = passwdtyp[2].split('@')[0]
                    restpath = passwdtyp[2].split('@')[1]
                    myproxy = restpath.split('/')[0]
                    ftppath = restpath.split('/')[1]
                    login = passwdtyp[1].split('//')[1]
                    dst = os.path.join(archivepath,fname)
                    fh = NamedTemporaryFile(suffix=suffix,delete=False)
                    print "Fi: ", fi
                    fh.write(urllib2.urlopen(fi).read())
                    fh.close()
                    shutil.move(fh.name,dst)
                    if (typus == 'ftp'):
                        ftpremove (ftppath=ftppath, filestr=fname, myproxy=myproxy, port=port, login=login, passwd=passwd)
        #start = iterationtime
        #iterationtime = date2num(num2date(iterationtime).replace(tzinfo=None)+timedelta(days=30))    

    st = st.sorting()
    
    loggerabs.info('--- Finished absolute analysis at %s ' % str(datetime.now()))
                            
    return st



def absoluteAnalysis(absdata, variodata, scalardata, **kwargs): 
    """
    DEFINITION:
        Analyze absolute data from files or database and create datastream

    PARAMETERS:
    Variables:
        - header_dict:  (dict) dictionary with header information 
    Kwargs:
        - starttime:    (string/datetime) define begin
        - endtime:      (string/datetime) define end
        - abstype:      (string) default manual, can be autodif
        - db:   	(mysql database) defined by MySQLdb.connect().
        - dbadd:        (bool) if True and read files will be added to the database
        - alpha:        (float) orientation angle 1 in deg (if z is vertical, alpha is the horizontal rotation angle)
        - beta:         (float) orientation angle 2 in deg 
        - deltaF:       (float) difference between scalar measurement point and pier (TODO: check the sign)
        - diid:         (string) identifier (id) of di files (e.g. A2_WIC.txt)
        - outputformat: (string) one of 'idf', 'xyz', 'hdf'
        - usestep:      (int) which step to use for analysis, usually both, in autodif only 2
        - annualmeans:  (list) provide annualmean for x,y,z as [x,y,z] with floats
        - azimuth:      (float) required for Autodif measurements
        - movetoarchive:(string) define a local directory to store archived data
    RETURNS:
        --
    EXAMPLE:
        (1) >>> stream = absoluteAnalysis('/home/leon/Dropbox/Daten/Magnetism/DI-WIC/autodif',variopath,'',abstype='autodif',azimuth=267.4242,starttime='2014-02-10',endtime='2014-02-25')
        (2) >>> stream = absoluteAnalysis('DIDATA_WIK',variopath,'',starttime='2013-12-20',endtime='2013-12-30',db=db)
        (3) >>> stream = absoluteAnalysis('/home/leon/Dropbox/Daten/Magnetism/DI-WIC/raw/',variopath,scalarpath,diid='A2_WIC.txt',starttime='2014-02-10',endtime='2014-02-25',db=db,dbadd=True)

    PERFORMED TESTS:
        (OK)1. Read data from database and files
        (OK)2. Read data from autodif and manual analysis 
        (OK)3. Put data to database (dbadd) 
        (OK)4. Check parameter for all possibilities: a) no db, b) db, c) db and override by input
        5. Archiving function
        6. Appropriate information on failed analyses
        7. is the usestep variable correctly applied for autodif and normal?
        8. overwrite of existing database lines?
      
    """
    db = kwargs.get('db')
    dbadd = kwargs.get('dbadd')
    alpha = kwargs.get('alpha')
    starttime = kwargs.get('starttime')
    endtime = kwargs.get('endtime')
    beta = kwargs.get('beta')
    stationid = kwargs.get('stationid')
    pier = kwargs.get('pier')
    deltaF = kwargs.get('deltaF')
    diid = kwargs.get('diid')
    outputformat = kwargs.get('outputformat')
    usestep = kwargs.get('usestep')
    annualmeans = kwargs.get('annualmeans')
    azimuth = kwargs.get('azimuth') # 267.4242 # A16 to refelctor
    abstype = kwargs.get('abstype')
    movetoarchive = kwargs.get('movetoarchive')

    if not outputformat:
        outputformat='idf'
    if not annualmeans:
        annualmeans=[20000,1200,43000]
    if not abstype:
        abstype = "manual"
    if abstype == 'autodif': # we also check the person given in the file. if this is AutoDIF abstype will be set correctly automatically
        usestep=2
        if not azimuth:
            print "Azimuth needs ro be provided for AutoDIF measurements"
            return

    # ####################################
    # 1. Get parameters from db or input (input overrides)
    # ####################################
    if db: 
        cursor = db.cursor()
        # Get all othere relevant data first before trying to read table (only if not provided by the user)
        try:
            if not stationid:
                stationid =  dbgetstring(db, 'DATAINFO', vario, 'StationID')
        except:
            pass
        try:
            if not pier:
                pier = dbgetstring(db, 'DATAINFO', vario, 'DataDeltaReferencePier')
        except:
            pass
        try:
            if not alpha:
                alpha =  dbgetfloat(db, 'DATAINFO', vario, 'DataSensorAzimuth')
        except:
            pass
        try:
            if not beta:
                beta =  dbgetfloat(db, 'DATAINFO', vario, 'DataSensorTilt')
        except:
            pass
        try:
            if not deltaF:
                deltaF =  dbgetfloat(db, 'DATAINFO', scalar, 'DataDeltaF')
        except:
            pass

    if not alpha: 
        alpha=0.0
    if not beta:
        beta=0.0
    if not deltaF:
        deltaF=0.0
    if not stationid:
        stationid=''
    if not pier:
        pier=''
    if not diid:
        diid=".txt"

    # Please Note for pier information always the existing pier in the file is used
    print "Using the following parameters (alpha, beta, stationid, pier, deltaF, diid):", alpha, beta, stationid, pier, deltaF, diid

    # ####################################
    # 2. Get absolute data
    # ####################################

    # 2.1 Database or File -> Get a datelist
    # --------------------
    readfile = True
    filelist, datelist = [],[]
    failinglist = []
    if db:        
        # Check whether absdata exists as table
        cursor.execute("SHOW TABLES LIKE '%s'" % absdata)
        try:
            value = cursor.fetchone()[0]
            # Found a table - now reading it and setting file read to zero
            try:
                sql = "SELECT StartTime FROM " + value
                cursor.execute(sql)
                values = cursor.fetchall()
                lst = [elem[0].split()[0] for elem in values]
                datelist = list(set(lst))
            except:
                print "absoluteAnalysis: Error while getting Absdata from db"
                return
            # DI TABLE FOUND
            readfile = False
        except:
            pass
        
    if readfile:
        # Get list of files
        # XXX ftp and url access
        if os.path.isfile(absdata):
            print "Found single file"
            filelist.append(absdata)
        else:
            for file in os.listdir(absdata):
                if file.endswith(diid):
                    filelist.append(os.path.join(absdata,file))

        for elem in filelist:
            head, tail = os.path.split(elem)
            try:
                date = dparser.parse(tail,fuzzy=True)
                datelist.append(datetime.strftime(date,"%Y-%m-%d"))
            except:
                print "absoluteAnalysis: Found date problem in file: %s" % tail
                failinglist.append(elem)

        datelist = list(set(datelist))

    datetimelist = [datetime.strptime(elem,'%Y-%m-%d') for elem in datelist]

    empty = DataStream()
    if starttime:
        datetimelist = [elem for elem in datetimelist if elem >= empty._testtime(starttime)]
    if endtime:
        datetimelist = [elem for elem in datetimelist if elem <= empty._testtime(endtime)]

    if not len(datetimelist) > 0:
        print "absoluteAnalysis: No matching dates found - aborting"
        return

    # 2.2 Cycle through datetimelist 
    # --------------------
    # read varios, scalar and all absfiles of one day
    # analyze data for each day and append results to a resultstream    
    # XXX possible issues: an absolute measurement which is performed in two day (e.g. across midnight)
    resultstream = DataStream()
    for date in sorted(datetimelist):
        variofound = True
        scalarfound = True
        print date
        # a) Read variodata
        print "-----------------"
        print "Reading Variodata"
        variostr = read(variodata,starttime=date,endtime=date+timedelta(days=1))
        print "Variolength:", len(variostr)
        if len(variostr) > 3: # can contain ([], 'File not specified')
            variostr =variostr.rotation(alpha=alpha, beta=beta)
            vafunc = variostr.interpol(['x','y','z'])
        else:
            print "absoluteAnalysis: no variometer data available"
            variofound = False
            
        # b) Load Scalardata
        print "-----------------"
        print "Reading Scalars"
        scalarstr = read(scalardata,starttime=date,endtime=date+timedelta(days=1))
        print "Scalarlength:", len(scalarstr)
        if len(scalarstr) > 3: # Because scalarstr can contain ([], 'File not specified')
            scfunc = scalarstr.interpol(['f'])
        else:
            print "absoluteAnalysis: no scalar data available"
            scalarfound = False

        # c) get absolute data
        abslist = []
        if readfile:
            datestr = datetime.strftime(date,"%Y-%m-%d")
            datestr2 = datetime.strftime(date,"%Y%m%d") # autodif
            print "Starting caclulation"
            print "-------------------------------------------------"
            print datestr
            if abstype == 'autodif':
                difiles = [di for di in filelist if datestr2 in di]
            else:
                difiles = [di for di in filelist if datestr in di]
            if len(difiles) > 0:
                for elem in difiles:
                    absst = absRead(elem,azimuth=azimuth,pier=pier,output='DIListStruct')
                    print "LENGTH:",len(absst)
                    try:
                        if not len(absst) > 1:
                            stream = absst[0].getAbsDIStruct()
                            abslist.append(absst)
                            if db and dbadd:
                                print "stationid", stationid
                                diline2db(db, absst,mode='insert',tablename='DIDATA_'+stationid)
                        else:
                            for a in absst:
                                stream = a.getAbsDIStruct()
                                abslist.append(a)
                            if db and dbadd:
                                diline2db(db, absst,mode='insert',tablename='DIDATA_'+stationid)
                    except:
                        print "absoluteAnalysis: Failed to analyse %s" % elem 
                        failinglist.append(elem)
                        # TODO Drop that line from filelist
                        pass
        else:
            #get list from database
            startd = datetime.strftime(date,"%Y-%m-%d")
            endd = datetime.strftime(date+timedelta(days=1),"%Y-%m-%d")
            #pier = 'D'
            #stationid = 'WIK'
            sql = "Pier='%s'" % pier
            tablename = 'DIDATA_%s' % stationid
            #print sql, tablename
            abslist = db2diline(db,starttime=startd,endtime=endd,sql=sql,tablename=tablename)

        for absst in abslist:
            print "-----------------"
            print "Analyzing %s measurement from %s" % (abstype,str(date))
            #if readfile:
            try:
                stream = absst[0].getAbsDIStruct()
            except:
                stream = absst.getAbsDIStruct()
            # if usestep not given and AutoDIF measruement found
            if stream[0].person == 'AutoDIF' and not usestep:
                usestep = 2
            print "USESTEP:", usestep
            if variofound:
                stream = stream._insert_function_values(vafunc)
            if scalarfound:
                stream = stream._insert_function_values(scfunc,funckeys=['f'],offset=deltaF)
            result = stream.calcabsolutes(usestep=usestep,annualmeans=annualmeans,printresults=True,debugmode=False)
       
            resultstream.add(result)

    # ####################################
    # 3. Format output
    # ####################################

    # 3.1 Header information 
    # --------------------
    resultstream.header['col-time'] = 'Epoch'
    resultstream.header['col-x'] = 'i'
    resultstream.header['unit-col-x'] = 'deg'
    resultstream.header['col-y'] = 'd'
    resultstream.header['unit-col-y'] = 'deg'
    resultstream.header['col-z'] = 'f'
    resultstream.header['unit-col-z'] = 'nT'
    resultstream.header['col-f'] = 'f'
    resultstream.header['col-dx'] = 'basex'
    resultstream.header['col-dy'] = 'basey'
    resultstream.header['col-dz'] = 'basez'
    resultstream.header['col-df'] = 'dF'
    resultstream.header['col-t1'] = 'T'
    resultstream.header['col-t2'] = 'ScaleValueDI'
    resultstream.header['col-var1'] = 'Dec_S0'
    resultstream.header['col-var2'] = 'Dec_deltaH'
    resultstream.header['col-var3'] = 'Dec_epsilonZ'
    resultstream.header['col-var4'] = 'Inc_S0'
    resultstream.header['col-var5'] = 'Inc_epsilonZ'
    resultstream.header['col-str1'] = 'Person'
    resultstream.header['col-str2'] = 'DI-Inst'
    resultstream.header['col-str3'] = 'F-Inst'
    resultstream.header['col-str4'] = 'Vario-Inst'

    if outputformat == 'xyz':
        #for elem in st:
        result = result.idf2xyz()
        result.typ = 'xyzf'         
        resultstream.header['col-x'] = 'x'
        resultstream.header['unit-col-x'] = 'nT'
        resultstream.header['col-y'] = 'y'
        resultstream.header['unit-col-y'] = 'nT'
        resultstream.header['col-z'] = 'z'
        resultstream.header['unit-col-z'] = 'nT'
    elif outputformat == 'hdz':
        #for elem in st:
        result = result.idf2xyz()
        #for elem in st:
        result = result.xyz2hdz()
        result.typ = 'hdzf'         
        resultstream.header['col-x'] = 'h'
        resultstream.header['unit-col-x'] = 'nT'
        resultstream.header['col-y'] = 'd'
        resultstream.header['unit-col-y'] = 'deg'
        resultstream.header['col-z'] = 'z'
        resultstream.header['unit-col-z'] = 'nT'

    # 3.2 Eventually archive the data 
    # --------------------
    # XXX possible issues: direct ftp reading or url reading
    if movetoarchive:
        if readfile:
            for fi in filelist:
                print fi     
                if not "://" in fi: 
                    src = fi
                    fname = os.path.split(src)[1]
                    dst = os.path.join(archivepath,fname)
                    shutil.move(src,dst)
                else:
                    fname = fi.split('/')[-1]
                    suffix = fname.split('.')[-1]
                    passwdtyp = fi.split(':')
                    typus = passwdtyp[0]
                    port = 21
                    passwd = passwdtyp[2].split('@')[0]
                    restpath = passwdtyp[2].split('@')[1]
                    myproxy = restpath.split('/')[0]
                    ftppath = restpath.split('/')[1]
                    login = passwdtyp[1].split('//')[1]
                    dst = os.path.join(archivepath,fname)
                    fh = NamedTemporaryFile(suffix=suffix,delete=False)
                    print "Fi: ", fi
                    fh.write(urllib2.urlopen(fi).read())
                    fh.close()
                    shutil.move(fh.name,dst)
                    if (typus == 'ftp'):
                        ftpremove (ftppath=ftppath, filestr=fname, myproxy=myproxy, port=port, login=login, passwd=passwd)

    resultstream = resultstream.sorting()

    print "Failed files:"
    print "---------------------------"
    for elem in failinglist:
        print elem

    return resultstream





def getAbsFilesFTP(**kwargs):
    """
    Obtain files from the selected directory
    Requires an analysis and an archive directory for treatment of downloaded absolute files
    Analysis directory:
    - contains the newly downloaded files. These files are then analyzed in in case of success transfered to the Archive directory.
    Archive directory:
    - contains successfully analyzed data (requires on errors and variometer correction)
    - downloaded data is checked, whether files are already exist in the archive directory. If true, they are deleted from the ftp server
    Keywords:
    localpath
    ftppath
    filestr(ing)
    myproxy
    port
    login
    passwd
    logfile
    archivepath
    """
    localpath = kwargs.get('localpath')
    ftppath = kwargs.get('ftppath')
    filestr = kwargs.get('filestr')
    myproxy = kwargs.get('myproxy')
    port = kwargs.get('port')
    login = kwargs.get('login')
    passwd = kwargs.get('passwd')
    logfile = kwargs.get('logfile')
    analysispath = kwargs.get('analysispath')
    archivepath = kwargs.get('archivepath')
    absidentifier = kwargs.get('absidentifier') # Part of filename, which defines absolute files

    if not absidentifier:
        absidentifier = '*AbsoluteMeas.txt'

    filelist = []
    
    msg = PyMagLog()
    loggerabs.info(" -- Starting downloading Absolute files from %s" % ftppath)

    # -- Checking whether new data is available
    ftplist = ftpdirlist (localpath=localpath, ftppath=ftppath, filestr=filestr, myproxy=myproxy, port=port, login=login, passwd=passwd, logfile=logfile)
    if len(ftplist) == 0:
        loggerabs.info(" ---- AbsDownload: no new data on ftp directory")
    # -- get local list
    for infile in iglob(os.path.join(archivepath,absidentifier)):
        filelist.append(infile)

    # -- Download files to Analysis folder
    for f in ftplist:
        loggerabs.info(" ---- Now getting %s" % f) 
        ftpget (localpath=analysispath, ftppath=ftppath, filestr=f, myproxy=myproxy, port=port, login=login, passwd=passwd, logfile=logfile)

    loggerabs.info(" -- Download procedure finished at %s" % ftppath)

    return ftpfilelist, localfilelist

def removeAbsFilesFTP(**kwargs):
    """
    Remove files from the selected directory
    Requires an analysis and an archive directory for treatment of downloaded absolute files
    Analysis directory:
    - contains the newly downloaded files. These files are then analyzed in in case of success transfered to the Archive directory.
    Archive directory:
    - contains successfully analyzed data (requires on errors and variometer correction)
    - downloaded data is checked, whether files are already exist in the archive directory. If true, they are deleted from the ftp server
    Keywords:
    ftppath
    filestr(ing)
    myproxy
    port
    login
    passwd
    ftpfilelist
    localfilelist
    """
    ftppath = kwargs.get('ftppath')
    filestr = kwargs.get('filestr')
    myproxy = kwargs.get('myproxy')
    port = kwargs.get('port')
    login = kwargs.get('login')
    passwd = kwargs.get('passwd')
    ftpfilelist = kwargs.get('ftpfilelist')
    localfilelist = kwargs.get('localfilelist')

    msg = PyMagLog()
    loggerabs.info(" -- Starting removing already successfully analyzed files from %s" % ftppath)

    doubles = list(set(ftpfilelist) & set(localfilelist))
    print doubles

    for f in doubles:
        ftpremove (ftppath=ftppath, filestr=f, myproxy=myproxy, port=port, login=login, passwd=passwd)

    loggerabs.info(" -- Removing procedure finished at %s" % ftppath)


# ##################
# ------------------
# Main program
# ------------------
# ##################

localpath = os.path.normpath(r'e:\leon\Programme\Python\PyMag\ExperimentalFolder')
ftppath = '/cobenzlabs'
filestr = 'test'
#myproxy = '94.136.40.103'
#port = 21
login = 'data@conrad-observatory.at'
myproxy = '138.22.156.44'
#port = 8021
login = 'data@conrad-observatory.at@94.136.40.103'


if __name__ == '__main__':
    print "Starting a test of the Absolutes program:"
    #msg = PyMagLog()
    # getAbsFTP()
    #st = analyzeAbsFiles(path_or_url=testpath, variopath=variopath, scalarpath=variopath)
    #st = analyzeAbsFiles(path_or_url=os.path.normpath(r'e:\leon\Programme\Python\PyMag\ExperimentalFolder'), alpha=3.25, beta=0.0, variopath=variopath, scalarpath=scalarpath)
    #st = analyzeAbsFiles(path_or_url=os.path.normpath(r'e:\leon\Programme\Python\PyMag\ExperimentalFolder'), alpha=3.25, beta=0.0, variopath=os.path.normpath('..\\dat\\lemi025\\*'), scalarpath=os.path.normpath('..\\dat\\didd\\*'), archivepath=os.path.normpath('..\\dat\\absolutes\\analyzed'))
    #st.write(analysispath,coverage='all',mode='replace',filenamebegins='absolutes_didd')

    #loglst = msg.combineWarnLog(msg.warnings,msg.logger)
    #print loglst

    #newst = read(path_or_url=summarypath)
    #newst.plot(['x','y','z'])
    #print newst.header

    ### ToDo
    # test for input variations (e.g. no f, scalevals, lemi vs didd etc)
    # eventually develop plot routine for absstruct....


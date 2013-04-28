# Copyright (C) 2010 Francois Pinot
#
# This code is free software; you can redistribute it
# and/or modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This code is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this code; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# 02111-1307 USA
#

import os
import ctypes
import csnd

class CsoundSession(csnd.Csound):
    """A class for running a csound session"""
    
    def __init__(self, csdFileName=None):
        """Start a csound session, eventually loading a csd file"""
        csnd.Csound.__init__(self)
        self.pt = None
        if csdFileName and os.path.exists(csdFileName):
            self.csd = csdFileName
            self.startThread()
        else:
            self.csd = None
    
    def startThread(self):
        if self.Compile(self.csd) == 0 :
            self.pt = csnd.CsoundPerformanceThread(self)
            self.pt.Play()
            
    def resetSession(self, csdFileName=None):
        """Reset the current session, eventually loading a new csd file"""
        if csdFileName and os.path.exists(csdFileName):
            self.csd = csdFileName
        if self.csd:
            self.stopPerformance()
            self.startThread()
    
    def stopPerformance(self):
        """Stop the current score performance if any"""
        if self.pt:
            if self.pt.GetStatus() == 0:
                self.pt.Stop()
            self.pt.Join()
            self.pt = None
        self.Reset()

    def getCsdFileName(self):
        """Return the loaded csd filename or None"""
        return self.csd
        
    def note(self, pvals, absp2mode = 0):
        """Send a score note to a csound instrument"""
        n = len(pvals)
        if csnd.csoundGetSizeOfMYFLT() == 8:
            pfields = csnd.doubleArray(n)
        else:
            pfields = csnd.floatArray(n)
        for i in xrange(n):
            pfields[i] = pvals[i]
        return self.pt.ScoreEvent(absp2mode, 'i', n, pfields)
        
    def scoreEvent(self, eventType, pvals, absp2mode = 0):
        """Send a score event to csound"""
        n = len(pvals)
        if csnd.csoundGetSizeOfMYFLT() == 8:
            pfields = csnd.doubleArray(n)
        else:
            pfields = csnd.floatArray(n)
        for i in xrange(n):
            pfields[i] = pvals[i]
        self.pt.ScoreEvent(absp2mode, eventType, n, pfields)
    
    def getTableBuffer(self, num):
        """Return a buffer pointing to the stored data of an ftable or raise an exception"""
        if self.TableLength(num) > 0:
            tbl = csnd.CsoundMYFLTArray()
            tblSize = self.GetTable(tbl.GetPtr(), num) + 1  # don't forget the guard point!
            if csnd.csoundGetSizeOfMYFLT() == 8:
                myflt = ctypes.c_double
            else:
                myflt = ctypes.c_float
            return ctypes.ARRAY(myflt, tblSize).from_address(tbl.GetPtr(0).__long__())
        else:
            raise(ValueError("ftable number %d does not exist!" % (num)))

    def flushMessages(self):
        """Wait until all pending messages are actually received by the performance thread"""
        if self.pt:
            self.pt.FlushMessageQueue()


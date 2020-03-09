import os
import re
import logging


# Single consecutive frame range
# ------------------------------
class FrameRangeError(ValueError):
    pass


class FrameRange(object):
    """FrameRange(object):
        def __init__(self, start, stop=None, step=None):
    
    This class represents a contiguous frame range from start to stop, INCLUSIVE, with an optional
    frame step.
    
    Start can be a string that will be parsed, or an iterable of 2 or 3 ints.
    If a string is given that cannot be parsed, or stop < start, FrameRangeError will be raised.
    """
    _pat = re.compile(ur"""(?P<start>-?\d+)-(?P<stop>-?\d+)(?:x(?P<step>\d+))?""")

    __slots__ = ("__weakref__", "_rng")

    def __init__(self, start, stop=None, step=None):
        if stop is None:
            if hasattr(start, "ituple"):
                # Also for subclasses of FrameRange
                start,stop,step = start.ituple
            elif hasattr(start, "__iter__"):
                # A list or tuple of endpoints and optional step, like (1,) or (1,10) or (1,10,2)
                start = tuple(start)
                if len(start) > 3:
                    raise FrameRangeError("expected start,stop,step: not %d-item sequence" %len(start))
                start,stop,fx = (start + (stop,None,None))[:3]
                step = fx or step
            else:
                # A frame range string
                dic = getattr(self._pat.search(str(start)), "groupdict", dict)()
                if dic:
                    start = dic["start"]
                    stop = dic.get("stop")
                    step = dic.get("step")
                elif isinstance(start, (int,long,float)) or start.isdigit() or \
                 (start and start[0] == '-' and start[1:].isdigit()):
                    stop = start
                    step = 1
                else:
                    raise FrameRangeError("bad frame range string: %s" %start)
        start = int(start)
        stop = int(stop or 0)
        step = max(1, min(int(step or 1), stop - start + 1))
        self._rng = (start, stop+1, step)
        if stop < start:
            raise FrameRangeError("bad frame range: %s" %self)

    # string reps
    # ------------------------------
    def __repr__(self):
        return "%s(%d,%d,%d)" %(self.__class__.__name__, self.start, self.stop, self.step)

    def __str__(self):
        if self.issingleframe: return str(self.start)
        return self.fullstr

    @property
    def fullstr(self):
        if self.step == 1:
            return "%d-%d" %(self.start, self.stop)
        return "%d-%dx%d" %(self.start, self.stop, self.step)

    # comparisons
    # ------------------------------  
    def __iter__(self):
        return iter(self.xrange())

    def __contains__(self, fr):
        if fr < self._rng[0] or fr >= self._rng[1]: return False
        return fr in self.xrange()

    def __len__(self):
        x = ((self._rng[1] - self._rng[0]) + self.step-1) / self.step
        return max(0, x)

    def __eq__(self, obj):
        try:
            return self._rng == obj.tuple
        except AttributeError:
            return False

    def __ne__(self, obj):
        try:
            return self._rng != obj.tuple
        except AttributeError:
            return False

    def __hash__(self):
        return hash(self._rng)

    def __lt__(self, obj):
        return (self.start, self.stop, len(self)) < (obj.start, obj.stop, len(obj))

    def __gt__(self, obj):
        return (self.start, self.stop, len(self)) > (obj.start, obj.stop, len(obj))

    def __le__(self, obj):
        return (self.start, self.stop, len(self)) <= (obj.start, obj.stop, len(obj))

    def __ge__(self, obj):
        return (self.start, self.stop, len(self)) >= (obj.start, obj.stop, len(obj))

    # other props
    # ------------------------------
    def copy(self):
        return self.__class__(*self.ituple)

    @property
    def start(self):
        return self._rng[0]

    @property
    def stop(self):
        return self._rng[1]-1

    @property
    def step(self):
        return self._rng[2]

    @property
    def tuple(self):
        """tuple of frame start,exclusive stop,step for sequence of input files, or degenerate values.
        stop is NOT inclusive"""
        return self._rng

    @property
    def ituple(self):
        """tuple of frame start,inclusive stop,step for sequence of input files, or degenerate values.
        stop IS inclusive"""
        return (self.start, self.stop, self.step)

    @property    
    def issingleframe(self):
        """returns True if this frame range contains only one frame"""
        return len(self) == 1

    @property    
    def iscontiguous(self):
        """always returns True for FrameRange objects"""
        return True

    def range(self):
        return range(*self.tuple)

    def xrange(self):
        return xrange(*self.tuple)

class FrameRanges(object):
    """FrameRanges(object):
        __init__(self, *args):

    This class represents a sequence of frames with a minimum list of FrameRange objects.
    It can represent any sequence of frames, including an empty frame range.

    FrameRanges can be initialized with any number of FrameRange objects. Or it can be given
    a comma-separated string. In addition, frames can be excluded from the range using a tilde.
    For example these result in the same FrameRanges:
      print FrameRanges(FrameRange("1-10"), FrameRange("20-30"), FrameRange(16))
      print FrameRanges("1-30~11-19,16")

    FrameRange and FrameRanges can be added and excluded by using the add() or exclude() methods.
    """
    kRangeDelim = ','
    kExcludeDelim = '~'
    maxstep = 100

    def __init__(self, *args):
        self._ranges = []
        if len(args) == 1 and isinstance(args[0], (str,unicode)):
            # A frame range string of comma separated subranges
            txtRanges = args[0].split(self.__class__.kRangeDelim)
            args = []
            for txt in txtRanges:
                txt = [r.strip() for r in txt.split(self.__class__.kExcludeDelim)]
                if not txt[0]:
                    continue
                excludeRanges = [FrameRange(xtxt) for xtxt in txt[1:] if xtxt]
                if not excludeRanges:
                    args.append(FrameRange(txt[0]))
                else:
                    # Exclude frames from a subrange, and then add those FrameRange objects
                    subrng = FrameRanges(FrameRange(txt[0]))
                    subrng.exclude(*tuple(excludeRanges))
                    args.extend(subrng._ranges)
            args = tuple(args)
        self.add(*args)

    def _compress(self, frames):
        rngs = []
        while len(frames) >= 3:
            sor = min(frames)       # start of range
            eor = max(frames)       # end of range

            # Determine increment (assume step is always <= self.maxstep)
            step = 1
            while step < self.maxstep and sor+step+step <= eor:
                if sor+step in frames and sor+step+step in frames: break
                step += 1
            #print ">", step, sor+step, sor+step+step, step > self.maxstep, sor+step+step > eor
            if step > self.maxstep or sor+step+step > eor:
                rngs.append(FrameRange(sor))                    # Add single frame
                frames.remove(sor)
                continue

            # Test range
            frames.remove(sor)
            x = sor+step
            while x <= eor and x in frames:
                frames.remove(x)
                x += step

            # Create range
            eor = x-step
            if sor+step != eor:
                rngs.append(FrameRange(sor,eor,step))           # Add current range
            else:
                rngs.append(FrameRange(sor))                    # Add disjoint frame
                frames.add(eor)                                 # Put last one back
                continue
                
        # Add final disjoint frames
        while frames: 
            rngs.append(FrameRange(frames.pop()))               # Add single frame

        rngs.sort()
        return rngs

    def frameset(self):
        """frameset(self):
        Return set of expanded frames from all FrameRange objects.
        """
        return reduce(set.union, [set(rng) for rng in self._ranges], set())
        
    def missing(self):
        frames = set(xrange(self.start, self.stop)) - self.frameset()
        return self.__class__(*tuple(self._compress(frames)))

    def _expandset(self, obj):
        if isinstance(obj, FrameRange):
            return set(obj)
        elif isinstance(obj, FrameRanges):
            return reduce(set.union, [set(rng) for rng in obj.iterranges()], set())
        raise TypeError("arguments must be FrameRange(s) objects: not %r" %obj)

    def add(self, *args):
        if not args:
            return
        # Expand frames and form union
        frames = reduce(set.union, [self._expandset(rng) for rng in args], self.frameset())
        self._ranges = self._compress(frames)

    def exclude(self, *args):
        if not args:
            return
        # Expand frames and subtract
        frames = self.frameset() - reduce(set.union, [self._expandset(rng) for rng in args])
        self._ranges = self._compress(frames)

    # string reps
    # ------------------------------
    def __repr__(self):
        return "%s(%r)" %(self.__class__.__name__, str(self))

    def __str__(self):
        return self.__class__.kRangeDelim.join([str(rng) for rng in self._ranges])

    @property
    def fullstr(self):
        return self.__class__.kRangeDelim.join([rng.fullstr for rng in self._ranges])

    # comparisons
    # ------------------------------  
    def __iter__(self):
        for rng in self._ranges:
            for fr in rng:
                yield fr

    def iterranges(self):
        return iter(self._ranges)

    def __contains__(self, fr):
        for _ in self:
            return True
        return False

    def __len__(self):
        return sum([len(rng) for rng in self._ranges])

    def __eq__(self, obj):
        try:
            if len(self._ranges) != len(obj._ranges):
                return False
            else:
                for a,b in zip(self._ranges, obj._ranges):
                    if a != b: return False
                else:
                    return True
        except AttributeError:
            return False

    def __ne__(self, obj):
        try:
            if len(self._ranges) != len(obj._ranges):
                return True
            else:
                for a,b in zip(self._ranges, obj._ranges):
                    if a != b: return True
                else:
                    return False
        except AttributeError:
            return False

    __hash__ = None

    def __lt__(self, obj):
        return (self.start, self.stop, len(self)) < (obj.start, obj.stop, len(obj))

    def __gt__(self, obj):
        return (self.start, self.stop, len(self)) > (obj.start, obj.stop, len(obj))

    def __le__(self, obj):
        return (self.start, self.stop, len(self)) <= (obj.start, obj.stop, len(obj))

    def __ge__(self, obj):
        return (self.start, self.stop, len(self)) >= (obj.start, obj.stop, len(obj))
        
    # other props
    #
    # @tuple, @ituple, & @xrange are all undefinied because a FrameRanges may have
    # many ranges and steps.
    # ------------------------------
    def copy(self):
        return self.__class__(*self._ranges)

    @property
    def start(self):
        if self._ranges:
            return self._ranges[0].start
        return None

    @property
    def stop(self):
        if self._ranges:
            return self._ranges[-1].stop
        return None

    @property    
    def step(self):
        if self.isempty:
            return None
        elif self.iscontiguous:
            return self._ranges[0].step
        else:
            #steps = set([rng.step for rng in self._ranges])
            #if len(steps) == 1:
            #    return steps.pop()
            raise FrameRangeError("step is undefined for non-contiguous %r" %self)

    @property    
    def issingleframe(self):
        """returns True if this frame range contains only one frame"""
        return len(self._ranges) == 1 and len(self._ranges[0]) == 1

    @property    
    def iscontiguous(self):
        """returns True if this is a contiguous frame range"""
        return len(self._ranges) <= 1

    @property    
    def isempty(self):
        """returns True if this frame range is empty"""
        return len(self._ranges) == 0

    def range(self):
        """range(self):
        Return all frames in order.
        """
        return sorted(reduce(list.__add__, [rng.range() for rng in self._ranges], []))

    # create FrameRanges object from rv syntax filepath
    # ------------------------------
    rv_frame_syntax_pat = re.compile(
        r"""(?:(?P<start>-?\d+)-(?P<stop>-?\d+)(?P<pad>#|@+)?)|(?:(?<=\D)(?P<single>-?\d+)?(?P<pad2>#|@+)(?=[.]))""")

    @classmethod
    def fromPath(kls, rvpath):
        """fromPath(kls, rvpath):
        Return a FrameRanges for files on disk that match rvpath with '#' or '@' wildcards.
        rvpath should be a pattern. A plain path without rv-style wildcards will raise an exception).
        
        The following rvpath examples are supported:
          Frames 1 to 100 no padding:     path/image.1-100@.jpg
          Frames 1 to 100 padding 4:      path/image.1-100#.jpg
                                       or path/image.1-100@@@@.jpg
          Frames 1 to 100 padding 5:      path/image.1-100@@@@@.jpg
          Frames -100 to -20 padding 4:   path/image.-100--20#jpg
          All Frames padding 4:           path/image.#.jpg
          All Frames padding 5:           path/image.@@@@@.jpg
        """
        base,fname = os.path.split(rvpath)
        fnd = kls.rv_frame_syntax_pat.search(fname)
        if fnd is None:
            raise FrameRangeError("bad rv frame range string: %s" %fname)

        dic = fnd.groupdict()

        txt = dic["pad"] or dic["pad2"]
        fpad = max(1, txt == '#' and 4 or len(txt or []))

        x,y = fnd.span()
        pre = fname[:x]
        post = fname[y:]

        frng = kls()                                    # empty FrameRanges
        if not dic["single"]:
            # specified range between start & stop
            fmin = dic["start"]
            if fmin is not None: fmin = int(fmin)
            fmax = dic["stop"]
            if fmax is not None: fmax = int(fmax)

            # Scan directory for files that match pat
            # File names are concatted into one long string
            pat = re.compile(r"""^%s(%s)%s$""" %(re.escape(pre), r"\d"*fpad, re.escape(post)), re.MULTILINE)
            files = '\n'.join([p for p in os.listdir(base or ".") if os.path.isfile(os.path.join(base, p))])
            logging.debug("matching %d files from: %s" %(len(files), base or os.getcwd()))

            frameset = set()
            for fnd in pat.finditer(files):
                fr = int(fnd.group(1))
                if fmin is not None and fr < fmin: continue
                if fmax is not None and fr > fmax: continue
                frameset.add(fr)

            frng._ranges = frng._compress(frameset)     # manually set frameset
        else:
            # specified single frame
            fr = int(dic["single"])
            p = os.path.join(base, "".join([pre, "%0*d" %(fpad, fr), post]))
            logging.debug("matching 1 file: %s" %p)
            if os.path.isfile(p):
                frng = kls(FrameRange(fr))
        return frng


### !!! Obsolete functions
# ------------------------------



def valid_frame_ranges(frame_ranges):
    '''
    Validate a multiple frame range definitions.
    @param frame_ranges string of the comma separated frame ranges to validate
    @return boolean to indicate validity, string of a valid frame range expression.
    '''

    ranges = frame_ranges.split(',')
    status = True
    for r in ranges:
        if not valid_frame_range(r):
            status = False

    str_ranges = ','.join(ranges)
    return status,str_ranges

def valid_frame_range(frame_range):
    '''
    Validate a frame range definition.

    Arguments:
    frame_range - string of the frame range to validate

    Returns:
    status - boolean to indicate validity.
    '''

    syntax = '^(\d+(-\d+(x\d+)*)*)+$'
    regex  = re.compile(syntax)

    if regex.match(frame_range):
        status = True
    else:
        status = False

    return status

def flat_frame_range(frame_range):
    '''
    Flat the frame ranges so we only see , separated string, ie 3, 5, 6-9 will be 3, 5, 6, 7, 8, 9
    Arguments:
    frame_range - string of the frame range to validate

    Returns:
    status - boolean to indicate validity.
    new_frame_range - flatted frame range
    '''
    status, frame_range = valid_frame_ranges(frame_range)
    if status:
        splited_frames = frame_range.split(',')
        sub_frames = []
        for sub_frame in splited_frames:
            if '-' in sub_frame:
                splited_sub_frame = sub_frame.split('-')
                start = splited_sub_frame[0]
                end = splited_sub_frame[1]
                step = 1
                if "x" in end:
                    end, step = end.split("x")
                for i in range(int(start), int(end)+1, int(step)):
                    sub_frames.append(str(i))
            else:
                sub_frames.append(sub_frame)
        frame_range = ','.join(sub_frames)
        return True, frame_range
    else:
        return False, frame_range

def is_static_frame_range(frame_ranges):
    '''
    Determine if a frame_range string represents a static frame range (i.e. just 1 frame).
    @param frame_ranges String of the comma separated frame ranges to check.
    @return True if the frame_ranges string represents a static frame range.  Otherwise, return False.
    '''
    status, frame_range_str = flat_frame_range(frame_ranges)
    if not status:
        return False
    frame_range_list = frame_range_str.split(',')
    if len(frame_range_list) == 1:
        return True
    return False


def get_fps():
    """
    @return The frame rate (frames per second) from the current host application.
    """
    try:
        import maya.cmds as cmds
    except:
        cmds = None

    fps = 24.0
    if cmds:
        currentFps = cmds.currentUnit( query=True, time=True )
        if currentFps == 'film':
            fps = 24.0
        elif currentFps == 'pal':
            fps = 25.0
        elif currentFps == 'show':
            fps = 48.0
        elif currentFps == 'palf':
            fps = 50.0
        elif currentFps == 'ntscf':
            fps = 60.0
        elif currentFps == 'game':
            fps = 15.0

        return fps

    try:
        import hou
    except:
        hou = None

    if hou:
        fps = hou.fps()

    return fps


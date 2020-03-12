import os
import re
import string
from collections import namedtuple
from dsk.base.tdata.gen_tree import GenTree
from pprint import pformat
from dsk.base.utils.msg_utils import MsgUtils as log
# some usefull query when version are in the cache
class version_db_context(namedtuple('versionDbcontext', "showobj entity is_shot")):
    __slots__ = ()

# some usefull query when version are in the cache
class version_date_compare(namedtuple('versiondatecompare', "v date")):
    __slots__ = ()
    @staticmethod
    def compare(a,b):
        return cmp(a.date,b.date)


class VersionInfoDb(GenTree):
    VC = ['deadlineMayaRender','delivery','publishedNukeRender','daily','hdri']
    VF2 = ['sg_version_number','sg_login',
          'sg_step', 'code', 'sg_status_list',
          'sg_path_to_frames', 'sg_path_to_movie',
          'created_at', 'description',
          'sg_first_frame', 'sg_last_frame']


    VF = ["code",
          "description",
          "entity",
          "frame_count",
          "frame_range",
          "id",
          "image",
          "project",
          "published_files",
          "sg_first_frame",
          "sg_last_frame",
          "sg_mg_is_latest",
          "sg_mg_sites",
          "sg_path_to_frames",
          "sg_path_to_movie",
          "sg_status_list",
          "sg_task",
          "sg_version_type",
          "user",
          "created_at",
          #"sg_version_number"
          ]
    VER_PATERN = re.compile("%sv[\d]*%s" % (os.sep,os.sep))
    VERP_PATERN = re.compile('\.v[\d]*\.')
    ## prod for non publish, temp for base on environment only
    VERP = re.compile('v[\d]*')

    INITBY = ['shotgun','prod','temp']
    #OFFSET = 100
    SOURCE_INFO = "source.info"
    PB_ROOT = "/tmp" # to detect playplast clip
    #main preference: use frame
    PREF_FRAME = True
    CROP = "-crop 80 45 880 495"

    PLeft = re.compile('\.l\.')
    DASH = "-"   # separator for frame

    @staticmethod
    def version_format(aint):
        return "%03d" % int(aint)

    @staticmethod
    def compare(a,b):
        """Version Compare"""
        return cmp(a.version_number, b.version_number)


    ####################### BASIC ############################
    def __repr__(self):
        return pformat(self.__dict__)

    def get_belong_to(self):
        return self._entity_belong

    def get_entity_query(self):
        return self.entity # shot or asset dict

    def getTypeName(self):
        """ for icon binding """
        if self.iconfile != "":
            return self.iconfile
        return self.getName()

    def __init__(self):
        super(VersionInfoDb, self).__init__()
        self.reset()

    def copy(self):
        s = VersionInfoDb()
        s.setName(self.getName())
        s.__dict__.update(self.__dict__)
        return s

    def copy_from(self,s):
        self.setName(s.getName())
        self.__dict__.update(s.__dict__)


    def isEnable(self):
        return self.enabled

    def setEnable(self,en):
        self.enabled = en

    def reset(self):
        self.id = -1                   # when from shotgun save the entity id
        self.enabled = True             # just a way to toggle on/off
        self.version_type = ""
        self.description = ""               # comment or notes
        self.path_to_frame = ""         # the full filename to the frames (as sequence)
        self.path_to_movie = ""         # the full filename to the movie
        self.thumbnailurl = ""
        self.iconfile = ""
        self.version_number = ""        # version number int
        self.version_str = ""
        self.creation_date = None
        self.first_frame = self.last_frame = -1
        self.frame_range = "0-0"
        self.task = ""
        self._entity_belong = ""

    ###############################################################################
    # SHOTGUN
    def setdata_shotgun(self, arg):
        """ use by shotgun query  """
        #print pformat(arg)

        self.id = arg.get('id',-1)

        n = arg.get('code',None)
        if n != None:
            self.setName(n.replace(" ","_"))
        else:
            self.setName("NO_NAME")
        self.version_type = arg.get('sg_version_type',"No_Type")
        if self.version_type == None:
            self.version_type = "No_Type"

        self.description = arg.get('description',"")
        if self.description == None:
            self.description = ""

        self.task = arg.get('sg_task',"")
        if self.task == None:
            self.task = ""

        self.path_to_frame = arg.get("sg_path_to_frames","")
        if self.path_to_frame == None:
            self.path_to_frame = ''

        self.path_to_movie = arg.get("sg_path_to_movie","")
        if self.path_to_movie == None:
            self.path_to_movie = ''



        data = ""
        if self.path_to_frame != "":
            self._useframe = True
            data = self.path_to_frame
        elif self.path_to_movie != "":
            self._useframe = False
            data = self.path_to_movie

        m = self.VER_PATERN.search(data)
        if m:
            self.version_number = int(m.group()[2:-1])  # dir version /v993/
            self.version_str = m.group()[1:-1]
        else:
            m = self.VERP_PATERN.search(self.getName())
            if m:
                self.version_number = int(m.group()[2:-1])  # name version .v993.
                self.version_str = m.group()[1:-1]
            else:
                m = self.VERP.search(self.getName())        # name version v999
                if m:
                    self.version_number = int(m.group()[1:])
                    self.version_str = m.group()
                else:
                    self.version_number = 1000
                    self.version_str = ""


        self.thumbnailurl = arg.get("image","")
        if self.thumbnailurl == None:
            self.thumbnailurl = ''

        self.status = arg.get("sg_status_list","na")
        if self.status == None:
            self.status = 'na'

        self.entity = arg.get("entity","")
        if self.entity == None:
            self.entity = {'name':'noentityname'}

        self.user = arg.get("user","")
        if self.user in [None,""]:
            self.user = {'name':'nousername'}


        self.creation_date = str(arg.get("created_at"))
        x = self.creation_date
        index = x.find(".")
        if index != -1:
            self.creation_date  = x[:index]

        self.first_frame = arg.get("sg_first_frame",-1)
        self.last_frame = arg.get("sg_last_frame",-1)
        self.frame_range = arg.get("frame_range","0-0")
        self.first_frame_cut = self.first_frame
        self.last_frame_cut = self.last_frame


        self._entity_belong = ""
        self._clean_belong()
        return True

    def _clean_belong(self):
        #remove entity from name
        x = self.getName()

        #remove all reference to entity name
        #### TO FIX BUG: some version mix the entity name with the name
        if self.entity['name'] != x:
            x = x.replace(self.entity['name'],"")

        #remove all reference to version number
        x = x.replace("%s" % self.version_str,"")
        #clean _

        x = x.replace("__","")
        x = x.replace("..","")
        if x.startswith("_"):
            x = x[1:]

        if x.endswith("_"):
            x = x[:-1]
        if x.startswith("."):
            x = x[1:]

        if x.endswith("."):
            x = x[:-1]
        self._entity_belong = x


    ################################# GET
    # api for widget
    def get_iconfile(self, db, location, base_res=64):
        """Return  iconfile. if iconfile == "", use thumbnailurl
            - download thumbnailurl
            - convert and resize image to png of the needed res

                :param location: a directory to download the image
                :param conn: a shotgun connection
                :param base_res: resolution in x, keep aspect

        """
        #from dskenv.api.envi_api import EnviApi

        if self.iconfile != "" and os.path.isfile(self.iconfile):
            return self.iconfile

        if self.thumbnailurl != "":
            dest = os.path.join(location, self.getName()+".jpg")
            #destpng = os.path.join(location, self.getName()+".png")
            destjpg = dest
            if not os.path.isfile(destjpg):
                try:
                    db.download_icon(self.thumbnailurl, dest)
                except Exception as e:
                    log.error(str(e))
                    return ""
            self.iconfile = destjpg

        return self.iconfile

    def get_creation_date(self):
        return self.creation_date

    def get_version(self):
        return self.version_number

    def get_dept(self):
        return self.step

    def get_author(self):
        return self.user['name']

    def get_status(self):
        return self.status

    def set_status(self,sta):
        self.status = sta

    def get_notes(self):
        if self.description == None:
            return ""
        return self.description

    def set_notes(self,data):
        self.description = str(data)
        return self.description

    def get_frame_range(self):
        return self.frame_range

    def get_frame_range_for_rv_api(self):
        return self.first_frame,self.last_frame

    def get_current_media(self):
        if VersionInfoDb.PREF_FRAME == True:
            if self._useframe == True and self.path_to_frame != "":
                return self.path_to_frame
            if self._useframe == False and self.path_to_movie != "":
                return self.path_to_movie
            if self.path_to_frame != "":
                return self.path_to_frame
            if self.path_to_movie != "":
                return self.path_to_movie
        else:
            if self.path_to_movie != "":
                return self.path_to_movie
            if self.path_to_frame != "":
                return self.path_to_frame
        return ""

    def is_movie(self):
        if self._useframe == False and self.path_to_movie != "":
            return True
        return False

    def is_left(self):
        a = self.get_current_media()
        m =  self.PLeft.search(a)
        if m:
            return True
        return False

    def has_frame(self):
        if self.path_to_frame != "":
            return True
        return False

    def has_movie(self):
        if self.path_to_movie != "":
            return True
        return False

    def get_all_versions(self):
        p_ver = self.getParent()
        if p_ver != None:
            return p_ver.getChildren()
        return list()

    #############################################################################
    # those function works in the context of versionobject being in the db tree
    #############################
    def get_versionlist_object(self):
        vobj = self.getParent()
        if vobj:
            return vobj.getParent()
        return None

    def get_entity_object(self):
        eobj = self.get_versionlist_object()
        if eobj:
            return eobj.getParent()
        return None

    def get_entity_name(self):
        return self.entity['name']

    def is_shot(self):
        return self.entity['type'] == 'Shot'

    def is_asset(self):
        return self.entity['type'] == 'Asset'

    def frame_exists(self):
        s = self.get_current_media()
        pp = os.path.dirname(s)
        if os.path.isdir(pp) == False:
            return False
        try:
            if len(os.listdir(pp)) == 0:
                return False
        except Exception as e:
            print(str(e))
            return False
        return True

    def is_overscanned(self):
        """No supported yet
        """
        return False

    def has_cut(self):
        if self.first_frame_cut != self.first_frame or self.last_frame_cut != self.last_frame:
            return True
        return False

    def get_frame_range_cut(self):
        if self.first_frame_cut == self.last_frame_cut:
            return ""
        return "%d%s%d" % (self.first_frame_cut, self.DASH, self.last_frame_cut)

    def get_frame_range_cut_rv(self):
        print((self.first_frame_cut == self.last_frame_cut))
        if self.first_frame_cut == self.last_frame_cut:
            return ""
        if self.first_frame_cut == self.first_frame and self.last_frame_cut == self.last_frame:
            return ""

        # regular for frame
        return "-in %d -out %d" % (self.first_frame_cut, self.last_frame_cut)

    def make_copy_and_update_if_temp(self):
        """ from playblast (temp file) with make a copy so when regenerated
        by playblast, rv doesn't get the new frame
        """
        moviefile = self.get_current_media()
        """
        if not moviefile.startswith(self.PB_ROOT):
            return moviefile
        moviefile = FrameSeqUtils.copy_sequence_temp(moviefile)
        """
        return moviefile
    @classmethod
    def get_audio_offset(cls,moviefile):
        pass

    def get_source_audio(self,afile):
        """ NO DONE
        """
        return ""
        if afile.endswith(".mov"):
            return ""
        audio = self.source_audio

        if audio != "":
            if os.path.exists(audio):
                return audio
            return ""
        return self.get_source_audio_with_meta(afile)

    @classmethod
    def get_source_audio_with_meta(cls, afile):
        dirname = ""
        root = ""
        try:
            dirname,root = os.path.split(afile)
        except:
            log.error("cannot get dirname from %r"  % afile)
            return ""
        rootl = root.split(".")
        root = ".".join(rootl[:-2])
        pp = os.path.join(dirname,root + "." + cls.SOURCE_INFO)

        if os.path.exists(pp):
            import yaml
            try:
                meta_mov = yaml.load(open(pp).read(),Loader=yaml.FullLoader)
                try:
                    return meta_mov['audio_path']
                except:
                    log.error("1 no audio_path key in file %s" % pp)

            except:
                log.error("1 cannot read audio_path %s" % pp)
        return cls.get_source_audio_with_meta_old(afile)
    @classmethod
    def get_source_audio_offset_with_meta(cls,afile = ""):
        """NOT DONE
        """
        return ""
        dirname = ""
        root = ""
        try:
            dirname,root = os.path.split(afile)
        except:
            log.error("cannot get dirname from %r"  % afile)
            return ""
        rootl = root.split(".")
        root = ".".join(rootl[:-2])
        pp = os.path.join(dirname,root + "." + cls.SOURCE_INFO)

        if os.path.exists(pp):
            import yaml
            try:
                meta_mov = yaml.load(open(pp).read(),Loader=yaml.FullLoader)
                return meta_mov['audio_offset']
            except:
                log.error("cannot read audio_offset %s" % pp)

        return cls.get_source_audio_offset_with_meta_old(afile)

    @classmethod
    def get_source_audio_offset_with_meta_old(cls,afile = ""):

        dirname = ""

        try:
            dirname = os.path.dirname(afile)
        except:
            log.error("cannot get dirname from %r"  % afile)
            return ""

        pp = os.path.join(dirname,cls.SOURCE_INFO)

        if os.path.exists(pp):
            import yaml
            try:
                meta_mov = yaml.load(open(pp).read())
                return meta_mov['audio_offset']
            except:
                log.error("cannot read audio_offset %s" % pp)

        return ""


SHOTGUN_ENTITY_TYPES = ['ActionMenuItem', 'ApiUser', 'AppWelcomeUserConnection', 'Asset', 'AssetAssetConnection',
                        'AssetBlendshapeConnection', 'AssetElementConnection', 'AssetEpisodeConnection',
                        'AssetLevelConnection', 'AssetLibrary', 'AssetMocapTakeConnection', 'AssetSceneConnection',
                        'AssetSequenceConnection', 'AssetShootDayConnection', 'AssetShotConnection', 'Attachment',
                        'BannerUserConnection', 'Blendshape', 'Booking', 'Camera', 'CameraMocapTakeConnection',
                        'Candidate', 'ClientUser', 'Cut', 'CutItem', 'CutVersionConnection', 'Delivery',
                        'DeliveryTarget', 'Delivery_sg_assets_Connection', 'Delivery_sg_shots_Connection',
                        'Delivery_sg_versions_Connection', 'Department', 'Element', 'ElementShotConnection', 'Episode',
                        'EventLogEntry', 'FilesystemLocation', 'Group', 'GroupUserConnection', 'HumanUser', 'Icon',
                        'Launch', 'LaunchSceneConnection', 'LaunchShotConnection', 'Level', 'LocalStorage', 'MocapPass',
                        'MocapSetup', 'MocapTake', 'MocapTakeRange', 'MocapTakeRangeShotConnection', 'Note', 'Page',
                        'PageHit', 'PageSetting', 'Performer', 'PerformerMocapTakeConnection',
                        'PerformerRoutineConnection', 'PerformerShootDayConnection', 'PermissionRuleSet', 'Phase',
                        'PhysicalAsset', 'PhysicalAssetMocapTakeConnection', 'PipelineConfiguration', 'Playlist',
                        'PlaylistShare', 'PlaylistVersionConnection', 'Project', 'ProjectUserConnection',
                        'PublishEvent', 'PublishedFile', 'PublishedFileDependency', 'PublishedFileType', 'Reel',
                        'Release', 'ReleaseTicketConnection', 'Reply', 'Revision', 'RevisionRevisionConnection',
                        'RevisionTicketConnection', 'Routine', 'RvLicense', 'Scene', 'Sequence', 'ShootDay',
                        'ShootDaySceneConnection', 'Shot', 'ShotShotConnection', 'Shot_sg_animations_Connection',
                        'Shot_sg_deliverables_Connection', 'Slate', 'SourceClip', 'Status', 'Step', 'TankAction',
                        'TankContainer', 'TankDependency', 'TankPublishedFile', 'TankType', 'Task', 'TaskDependency',
                        'TaskTemplate', 'TemerityNode', 'Ticket', 'TicketTicketConnection',
                        'Ticket_sg_related_assets_Connection', 'TimeLog', 'Tool', 'Version', 'WatermarkingPreset']

SHOTGUN_ENTITY_TYPES.extend(["CustomEntity%02d"%x for x in range(1, 51)])
SHOTGUN_ENTITY_TYPES.extend(["CustomNonProjectEntity%02d"%x for x in range(1, 31)])
SHOTGUN_ENTITY_TYPES.extend(["CustomThreadedEntity%02d"%x for x in range(1, 16)])

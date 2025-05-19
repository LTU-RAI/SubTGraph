## Content Description

### ConnectionHelper.cc
  Contains the opening connection coordinates and types
  * std::map<std::string, std::vector<ignition::math::Vector3d>>  **subt::ConnectionHelper::connectionPoints**
  * std::map<std::string, subt::ConnectionHelper::ConnectionType> **subt::ConnectionHelper::connectionTypes**

### world_generator_utils.cc
  Contains helpers for position and rotation transforms
  * void **TunnelTileRotations**(const std::string &_tileName, math::Vector3d &_pt, math::Quaterniond &_rot)

### world_generator_base.cc
  Contains helpers for download and selection of tiles from connection types
  * void **WorldGenerator::LoadTiles**()
  * WorldSection **WorldGenerator::SelectWorldSection**(TileType &_tileType)
      ```
        // Random selection of world sections with several tiles

        int r = rand() % this->worldSections.size();
        WorldSection s = this->worldSections[r]
      ```

### cave_generator.cc
  Contains the code for the generation of the mine environment
  * std::vector<WorldSection> **CaveGeneratorBase::CreateTypeAWorldSections**()
      ```
        // Create initial static set of world sections with type A tiles

        VertexData t;
        t.tileType = "Cave Vertical Shaft Straight Bottom Type A";
        t.model.SetRawPose(math::Pose3d(25, 0, 0, 0, 0, -1.5708));
        s.tiles.push_back(t);
      ```
  * std::vector<WorldSection> **CaveGeneratorBase::CreateTypeBWorldSections**(std::map<std::string, std::vector<ignition::math::Vector3d>> &_tileConnectionPoints)
      ```
        // Create initial static set of world sections with type B tiles

        VertexData t;
        t.tileType = "Cave Cavern Split 02 Type B";
        t.model.SetRawPose(math::Pose3d(halfTileSize, 0, 0, 0, 0, 0));
        s.tiles.push_back(t);
      ```
  * void **CaveGenerator::LoadTiles**()
      ```
        if (this->subWorldType == CAVE_ANASTOMOTIC || this->subWorldType == CAVE_CURVILINEAR)
        {
            this->CreateTransitionWorldSection();
            this->worldSections = this->CreateTypeAWorldSections();
        }
      ```
  * WorldSection **CaveGenerator::SelectWorldSection**(TileType &_tileType)
      ```
        // Set a 20% probablity of including a transition tile for curvilinear worlds
        if (rand() % 10 + 1 > 8)
            return this->transitionWorldSection;
      ```
  * void **CaveGenerator::Generate**()
      ```
        int attempt = 0;
        int maxAttempt = 20;
        while (!selected && attempt++ < maxAttempt) {
            ...
            // Do bounding box intersection check to prevent overlapping tiles
            if (this->IntersectionCheck(s, transform, this->addedWorldSections))
                continue;
            ...
        }
        ...
        // Fill all openings with caps
        int capNo = 1;
        std::string capUri = "https://fuel.ignitionrobotics.org/1.0/OpenRobotics/models/";
        std::string capUriTypeA = capUri + "Cave Cap Type A";
        std::string capUriTypeB = capUri + "Cave Cap Type B";
        ```

## Algorithmic Generation

1. Create initial world sections from predefined A-type/B-type blocks of tiles.
2. Loop through openings and add tiles to the connection points until specified tile count.
3. Attempt adding a tile to the current connection point until max number of attemts. 
   1. Apply transforms to selected tile for current opening.
   2. Bounding box intersection check to prevent overlapping tiles.
       * Failure to add a tile is mostly due to intersection with existing tiles in the world.
   3. Zero-opening tile check, only allowed during non-reached tile count.
   4. Update resulting openings in world.
4. Fill non-succesful opening assignments with caps.
5. Build .sdf file description from tile grid.
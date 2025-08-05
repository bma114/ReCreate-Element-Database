SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema element_database_phys
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema element_database_phys
-- -----------------------------------------------------
-- Drop existing database if it exists
DROP DATABASE IF EXISTS `element_database_phys`;

CREATE SCHEMA IF NOT EXISTS `element_database_phys` DEFAULT CHARACTER SET utf8 ;
USE `element_database_phys` ;

-- -----------------------------------------------------
-- Table `element_database_phys`.`Wall_Geometry`
-- -----------------------------------------------------
CREATE TABLE `Wall_Geometry` (
  `Product_ID` VARCHAR(30) NOT NULL,
  `total_height_mm` DECIMAL(10,3) NOT NULL,
  `total_length_mm` DECIMAL(10,3) NOT NULL,
  `total_thickness_mm` DECIMAL(10,3) NOT NULL,
  `density_kgm3` FLOAT NOT NULL,
  `element_volume_m3` FLOAT NOT NULL,
  `element_mass_kg` FLOAT NOT NULL,
  PRIMARY KEY (`Product_ID`),
  -- Foreign key back to core.Wall_Geometry
  CONSTRAINT `fk_phys_wall_geom_core`
    FOREIGN KEY (`Product_ID`)
    REFERENCES `element_database_core`.`Wall_Geometry` (`Product_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Table `element_database_phys`.`Beam_Geometry`
-- -----------------------------------------------------
CREATE TABLE `Beam_Geometry` (
  `Product_ID` VARCHAR(30) NOT NULL,
  `total_height_mm` DECIMAL(10,3) NOT NULL,
  `total_length_mm` DECIMAL(10,3) NOT NULL,
  `total_width_mm` DECIMAL(10,3) NOT NULL,
  `density_kgm3` FLOAT NOT NULL,
  `element_volume_m3` FLOAT NOT NULL,
  `element_mass_kg` FLOAT NOT NULL,
  PRIMARY KEY (`Product_ID`),
  -- Foreign key back to core.Beam_Geometry
  CONSTRAINT `fk_phys_beam_geom_core`
    FOREIGN KEY (`Product_ID`)
    REFERENCES `element_database_core`.`Beam_Geometry` (`Product_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Table `element_database_phys`.`Column_Geometry`
-- -----------------------------------------------------
CREATE TABLE `Column_Geometry` (
  `Product_ID` VARCHAR(30) NOT NULL,
  `total_height_mm` DECIMAL(10,3) NOT NULL,
  `total_depth_mm` DECIMAL(10,3) NULL,
  `total_width_mm` DECIMAL(10,3) NULL,
  `diameter_a_mm` FLOAT NULL,
  `diameter_b_mm` FLOAT NULL,
  `density_kgm3` FLOAT NOT NULL,
  `element_volume_m3` FLOAT NOT NULL,
  `element_mass_kg` FLOAT NOT NULL,
  PRIMARY KEY (`Product_ID`),
  -- Foreign key back to core.Column_Geometry
  CONSTRAINT `fk_phys_column_geom_core`
    FOREIGN KEY (`Product_ID`)
    REFERENCES `element_database_core`.`Column_Geometry` (`Product_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Table `element_database_phys`.`Slab_Geometry`
-- -----------------------------------------------------
CREATE TABLE `Slab_Geometry` (
  `Product_ID` VARCHAR(30) NOT NULL,
  `total_height_mm` DECIMAL(10,3) NOT NULL,
  `total_length_mm` DECIMAL(10,3) NOT NULL,
  `total_width_mm` DECIMAL(10,3) NOT NULL,
  `density_kgm3` FLOAT NOT NULL,
  `element_volume_m3` FLOAT NOT NULL,
  `element_mass_kg` FLOAT NOT NULL,
  PRIMARY KEY (`Product_ID`),
  -- Foreign key back to core.Slab_Geometry
  CONSTRAINT `fk_phys_slab_geom_core`
    FOREIGN KEY (`Product_ID`)
    REFERENCES `element_database_core`.`Slab_Geometry` (`Product_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Table `element_database_phys`.`Wall_Zone_Geometry`
-- -----------------------------------------------------
CREATE TABLE `Wall_Zone_Geometry` (
  `Zone_ID` VARCHAR(30) NOT NULL,
  `Reinf_ID` VARCHAR(30) NOT NULL,
  `Product_ID` VARCHAR(30) NOT NULL,
  `zone_height_mm` DECIMAL(10,3) NOT NULL,
  `zone_length_mm` DECIMAL(10,3) NOT NULL,
  `zone_thickness_mm` DECIMAL(10,3) NOT NULL,
  PRIMARY KEY (`Zone_ID`),
  -- Link back to the core Wall_Long_Reinf
  CONSTRAINT `fk_phys_zone_to_wall_long_zone`
    FOREIGN KEY (`Zone_ID`)
    REFERENCES `element_database_core`.`Wall_Long_Reinf` (`Zone_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  -- Link back to the core Wall_Long_Reinf via its Reinf_ID
  CONSTRAINT `fk_phys_zone_to_wall_long_reinf`
    FOREIGN KEY (`Reinf_ID`)
    REFERENCES `element_database_core`.`Wall_Long_Reinf` (`Reinf_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  -- Link back to the parent element in Wall_Geometry for dimensions
  CONSTRAINT `fk_phys_zone_to_wall_geom`
    FOREIGN KEY (`Product_ID`)
    REFERENCES `element_database_phys`.`Wall_Geometry` (`Product_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Table `element_database_phys`.`Beam_Zone_Geometry`
-- -----------------------------------------------------
CREATE TABLE `Beam_Zone_Geometry` (
  `Zone_ID` VARCHAR(30) NOT NULL,
  `Reinf_ID` VARCHAR(30) NOT NULL,
  `Product_ID` VARCHAR(30) NOT NULL,
  `zone_height_mm` DECIMAL(10,3) NOT NULL,
  `zone_length_mm` DECIMAL(10,3) NOT NULL,
  `zone_width_mm` DECIMAL(10,3) NOT NULL,
  PRIMARY KEY (`Zone_ID`),
  -- Link back to the core Beam_Long_Reinf
  CONSTRAINT `fk_phys_beam_zone_to_beam_long_zone`
    FOREIGN KEY (`Zone_ID`)
    REFERENCES `element_database_core`.`Beam_Long_Reinf` (`Zone_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  -- Link back to the core Beam_Long_Reinf via its Reinf_ID
  CONSTRAINT `fk_phys_beam_zone_to_beam_long_reinf`
    FOREIGN KEY (`Reinf_ID`)
    REFERENCES `element_database_core`.`Beam_Long_Reinf` (`Reinf_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  -- Link back to the parent element in Beam_Geometry for dimensions
  CONSTRAINT `fk_phys_zone_to_beam_geom`
    FOREIGN KEY (`Product_ID`)
    REFERENCES `element_database_phys`.`Beam_Geometry` (`Product_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Table `element_database_phys`.`Column_Zone_Geometry`
-- -----------------------------------------------------
CREATE TABLE `Column_Zone_Geometry` (
  `Zone_ID` VARCHAR(30) NOT NULL,
  `Reinf_ID` VARCHAR(30) NOT NULL,
  `Product_ID` VARCHAR(30) NOT NULL,
  `zone_height_mm` DECIMAL(10,3) NOT NULL,
  `zone_length_mm` DECIMAL(10,3) NOT NULL,
  `zone_width_mm` DECIMAL(10,3) NOT NULL,
  PRIMARY KEY (`Zone_ID`),
  -- Link back to the core Column_Long_Reinf
  CONSTRAINT `fk_phys_zone_to_col_long_zone`
    FOREIGN KEY (`Zone_ID`)
    REFERENCES `element_database_core`.`Column_Long_Reinf` (`Zone_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  -- Link back to the core Column_Long_Reinf via its Reinf_ID
  CONSTRAINT `fk_phys_zone_to_col_long_reinf`
    FOREIGN KEY (`Reinf_ID`)
    REFERENCES `element_database_core`.`Column_Long_Reinf` (`Reinf_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  -- Link back to the parent element in Column_Geometry for dimensions
  CONSTRAINT `fk_phys_zone_to_col_geom`
    FOREIGN KEY (`Product_ID`)
    REFERENCES `element_database_phys`.`Column_Geometry` (`Product_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Table `element_database_phys`.`Slab_Zone_Geometry`
-- -----------------------------------------------------
CREATE TABLE `Slab_Zone_Geometry` (
  `Zone_ID` VARCHAR(30) NOT NULL,
  `Reinf_ID` VARCHAR(30) NOT NULL,
  `Product_ID` VARCHAR(30) NOT NULL,
  `zone_height_mm` DECIMAL(10,3) NOT NULL,
  `zone_length_mm` DECIMAL(10,3) NOT NULL,
  `zone_thickness_mm` DECIMAL(10,3) NOT NULL,
  PRIMARY KEY (`Zone_ID`),
  -- Link back to the core Slab_Long_Reinf
  CONSTRAINT `fk_phys_zone_to_slab_long_zone`
    FOREIGN KEY (`Zone_ID`)
    REFERENCES `element_database_core`.`Slab_Long_Reinf` (`Zone_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  -- Link back to the core Slab_Long_Reinf via its Reinf_ID
  CONSTRAINT `fk_phys_zone_to_slab_long_reinf`
    FOREIGN KEY (`Reinf_ID`)
    REFERENCES `element_database_core`.`Slab_Long_Reinf` (`Reinf_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  -- Link back to the parent element in Slab_Geometry for dimensions
  CONSTRAINT `fk_phys_zone_to_slab_geom`
    FOREIGN KEY (`Product_ID`)
    REFERENCES `element_database_phys`.`Slab_Geometry` (`Product_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Table `element_database_phys`.`Corbel_Geometry`
-- -----------------------------------------------------
CREATE TABLE `Corbel_Geometry` (
  `Corbel_ID` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `Wall_Product_ID` VARCHAR(30) NULL,
  `Beam_Product_ID` VARCHAR(30) NULL,
  `Column_Product_ID` VARCHAR(30) NULL,
  `depth_mm` DECIMAL(10,3) NOT NULL,
  `length_mm` DECIMAL(10,3) NOT NULL,
  `midpoint_mm` DECIMAL(10,3) NOT NULL,
  `dist_from_top_mm` DECIMAL(10,3) NOT NULL,
  `rect_blk_height_mm` DECIMAL(10,3) NOT NULL,
  `tri_blk_height_mm` DECIMAL(10,3) NOT NULL,
  `center_h_offset_mm` DECIMAL(10,3) NOT NULL,
  `volume_m3` FLOAT NOT NULL,
  `mass_kg` FLOAT NOT NULL,
  PRIMARY KEY (`Corbel_ID`),
  -- link back to the Corbel_Geometry table that owns this corbel
  CONSTRAINT `fk_phys_corbel_to_core_corbel`
    FOREIGN KEY (`Corbel_ID`)
    REFERENCES `element_database_core`.`Corbel_Geometry` (`Corbel_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  -- informational link back to the parent element geometry
  CONSTRAINT `fk_phys_corbel_to_wall_core`
    FOREIGN KEY (`Wall_Product_ID`)
    REFERENCES `element_database_core`.`Corbel_Geometry` (`Wall_Product_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_phys_corbel_to_beam_core`
    FOREIGN KEY (`Beam_Product_ID`)
    REFERENCES `element_database_core`.`Corbel_Geometry` (`Beam_Product_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
CONSTRAINT `fk_phys_corbel_to_column_core`
    FOREIGN KEY (`Column_Product_ID`)
    REFERENCES `element_database_core`.`Corbel_Geometry` (`Column_Product_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Table `element_database_phys`.`Wall_Voids`
-- -----------------------------------------------------
CREATE TABLE `Wall_Voids` (
  `Void_ID` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `Product_ID` VARCHAR(30) NOT NULL,
  `base_v_offset_mm` DECIMAL(10,3) NOT NULL,
  `void_center_mm` DECIMAL(10,3) NOT NULL,
  `center_h_offset_mm` DECIMAL(10,3) NOT NULL,
  `height_mm` DECIMAL(10,3) NOT NULL,
  `length_mm` DECIMAL(10,3) NOT NULL,
  `depth_mm` DECIMAL(10,3) NOT NULL,
  `volume_m3` FLOAT NOT NULL,
  PRIMARY KEY (`Void_ID`),
  -- link back to the Wall_Voids table that owns this void
  CONSTRAINT `fk_phys_wall_void_to_core_void`
    FOREIGN KEY (`Void_ID`)
    REFERENCES `element_database_core`.`Wall_Voids` (`Void_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  -- informational link back to the parent element geometry
  CONSTRAINT `fk_phys_wall_void_to_geom_core`
    FOREIGN KEY (`Product_ID`)
    REFERENCES `element_database_phys`.`Wall_Geometry` (`Product_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Table `element_database_phys`.`Slab_Voids`
-- -----------------------------------------------------
CREATE TABLE `Slab_Voids` (
  `Void_ID` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `Product_ID` VARCHAR(30) NOT NULL,
  `base_v_offset_mm` DECIMAL(10,3) NOT NULL,
  `void_center_mm` DECIMAL(10,3) NOT NULL,
  `center_h_offset_mm` DECIMAL(10,3) NOT NULL,
  `height_mm` DECIMAL(10,3) NOT NULL,
  `length_mm` DECIMAL(10,3) NOT NULL,
  `depth_mm` DECIMAL(10,3) NOT NULL,
  `volume_m3` FLOAT NOT NULL,
  PRIMARY KEY (`Void_ID`),
  -- link back to the Slab_Voids table that owns this void
  CONSTRAINT `fk_phys_slab_void_to_core_void`
    FOREIGN KEY (`Void_ID`)
    REFERENCES `element_database_core`.`Slab_Voids` (`Void_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  -- informational link back to the parent element geometry
  CONSTRAINT `fk_phys_slab_void_to_geom_core`
    FOREIGN KEY (`Product_ID`)
    REFERENCES `element_database_phys`.`Slab_Geometry` (`Product_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Table `element_database_phys`.`Additional_Panelling`
-- -----------------------------------------------------
CREATE TABLE `Additional_Panelling` (
  `Product_ID` VARCHAR(30) NOT NULL,
  `panel_height_mm` DECIMAL(10,3) NOT NULL,
  `panel_length_mm` DECIMAL(10,3) NOT NULL,
  `panel_thickness_mm` DECIMAL(10,3) NOT NULL,
  `panel_volume_m3` FLOAT NOT NULL,
  `insul_height_mm` DECIMAL(10,3) NOT NULL,
  `insul_length_mm` DECIMAL(10,3) NOT NULL,
  `insul_thickness_mm` DECIMAL(10,3) NOT NULL,
  `insul_volume_m3` FLOAT NOT NULL,
  PRIMARY KEY (`Product_ID`),
  -- link back to the parent element geometry
  CONSTRAINT `fk_phys_panels_to_core_panels`
    FOREIGN KEY (`Product_ID`)
    REFERENCES `element_database_core`.`Additional_Panelling` (`Product_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Table `element_database_phys`.`Wall_Long_Reinf`
-- -----------------------------------------------------
CREATE TABLE `Wall_Long_Reinf` (
  `Long_ID` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `Reinf_ID` VARCHAR(30) NOT NULL,
  `bar_length_mm` DECIMAL(10,3) NOT NULL,
  `bar_area_mm2` DECIMAL(10,3) NOT NULL,
  `effective_depth_mm` DECIMAL(10,3) NOT NULL,
  PRIMARY KEY (`Long_ID`),
  -- Link back to the core Wall_Long_Reinf
  CONSTRAINT `fk_phys_long_to_wall_core_long`
    FOREIGN KEY (`Long_ID`)
    REFERENCES `element_database_core`.`Wall_Long_Reinf` (`Long_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  -- Link back to the phys Wall_Zone_Geometry via its Reinf_ID
  CONSTRAINT `fk_phys_long_to_wall_phys_zone`
    FOREIGN KEY (`Reinf_ID`)
    REFERENCES `element_database_phys`.`Wall_Zone_Geometry` (`Reinf_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Table `element_database_phys`.`Beam_Long_Reinf`
-- -----------------------------------------------------
CREATE TABLE `Beam_Long_Reinf` (
  `Long_ID` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `Reinf_ID` VARCHAR(30) NOT NULL,
  `bar_length_mm` DECIMAL(10,3) NOT NULL,
  `bar_area_mm2` DECIMAL(10,3) NOT NULL,
  `effective_depth_mm` DECIMAL(10,3) NOT NULL,
  PRIMARY KEY (`Long_ID`),
  -- Link back to the core Beam_Long_Reinf
  CONSTRAINT `fk_phys_long_to_beam_core_long`
    FOREIGN KEY (`Long_ID`)
    REFERENCES `element_database_core`.`Beam_Long_Reinf` (`Long_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  -- Link back to the phys Beam_Zone_Geometry via its Reinf_ID
  CONSTRAINT `fk_phys_long_to_beam_phys_zone`
    FOREIGN KEY (`Reinf_ID`)
    REFERENCES `element_database_phys`.`Beam_Zone_Geometry` (`Reinf_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Table `element_database_phys`.`Column_Long_Reinf`
-- -----------------------------------------------------
CREATE TABLE `Column_Long_Reinf` (
  `Long_ID` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `Reinf_ID` VARCHAR(30) NOT NULL,
  `bar_length_mm` DECIMAL(10,3) NOT NULL,
  `bar_area_mm2` DECIMAL(10,3) NOT NULL,
  `effective_depth_mm` DECIMAL(10,3) NOT NULL,
  PRIMARY KEY (`Long_ID`),
  -- Link back to the core Column_Long_Reinf
  CONSTRAINT `fk_phys_long_to_col_core_long`
    FOREIGN KEY (`Long_ID`)
    REFERENCES `element_database_core`.`Column_Long_Reinf` (`Long_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  -- Link back to the phys Column_Zone_Geometry via its Reinf_ID
  CONSTRAINT `fk_phys_long_to_col_phys_zone`
    FOREIGN KEY (`Reinf_ID`)
    REFERENCES `element_database_phys`.`Column_Zone_Geometry` (`Reinf_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Table `element_database_phys`.`Slab_Long_Reinf`
-- -----------------------------------------------------
CREATE TABLE `Slab_Long_Reinf` (
  `Long_ID` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `Reinf_ID` VARCHAR(30) NOT NULL,
  `bar_length_mm` DECIMAL(10,3) NOT NULL,
  `bar_area_mm2` DECIMAL(10,3) NOT NULL,
  `effective_depth_mm` DECIMAL(10,3) NOT NULL,
  PRIMARY KEY (`Long_ID`),
  -- Link back to the core Slab_Long_Reinf
  CONSTRAINT `fk_phys_long_to_slab_core_long`
    FOREIGN KEY (`Long_ID`)
    REFERENCES `element_database_core`.`Slab_Long_Reinf` (`Long_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  -- Link back to the phys Slab_Zone_Geometry via its Reinf_ID
  CONSTRAINT `fk_phys_long_to_slab_phys_zone`
    FOREIGN KEY (`Reinf_ID`)
    REFERENCES `element_database_phys`.`Slab_Zone_Geometry` (`Reinf_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Table `element_database_phys`.`Wall_Transv_Reinf`
-- -----------------------------------------------------
CREATE TABLE `Wall_Transv_Reinf` (
  `Transv_ID` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `Zone_ID` VARCHAR(30) NOT NULL,
  `Reinf_ID` VARCHAR(30) NOT NULL,
  `num_legs` VARCHAR(50) NOT NULL,
  `volumetric_ratio_mm3` VARCHAR(50) NOT NULL,
  PRIMARY KEY (`Transv_ID`),
  -- Link back to the core Wall_Transv_Reinf
  CONSTRAINT `fk_phys_transv_to_wall_core_transv`
    FOREIGN KEY (`Transv_ID`)
    REFERENCES `element_database_core`.`Wall_Transv_Reinf` (`Transv_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  -- Link back to the phys Wall_Zone_Geometry via its Zone_ID
  CONSTRAINT `fk_phys_transv_to_wall_phys_zone`
    FOREIGN KEY (`Zone_ID`)
    REFERENCES `element_database_phys`.`Wall_Zone_Geometry` (`Zone_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  -- Informational link to the overall Reinf_ID
  CONSTRAINT `fk_phys_transv_to_wall_core_reinf`
    FOREIGN KEY (`Reinf_ID`)
    REFERENCES `element_database_core`.`Wall_Transv_Reinf` (`Reinf_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Table `element_database_phys`.`Beam_Transv_Reinf`
-- -----------------------------------------------------
CREATE TABLE `Beam_Transv_Reinf` (
  `Transv_ID` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `Zone_ID` VARCHAR(30) NOT NULL,
  `Reinf_ID` VARCHAR(30) NOT NULL,
  `num_legs` VARCHAR(50) NOT NULL,
  `volumetric_ratio_mm3` VARCHAR(50) NOT NULL,
  PRIMARY KEY (`Transv_ID`),
  -- Link back to the core Beam_Transv_Reinf
  CONSTRAINT `fk_phys_transv_to_beam_core_transv`
    FOREIGN KEY (`Transv_ID`)
    REFERENCES `element_database_core`.`Beam_Transv_Reinf` (`Transv_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  -- Link back to the phys Beam_Zone_Geometry via its Zone_ID
  CONSTRAINT `fk_phys_transv_to_beam_phys_zone`
    FOREIGN KEY (`Zone_ID`)
    REFERENCES `element_database_phys`.`Beam_Zone_Geometry` (`Zone_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  -- Informational link to the overall Reinf_ID
  CONSTRAINT `fk_phys_transv_to_beam_core_reinf`
    FOREIGN KEY (`Reinf_ID`)
    REFERENCES `element_database_core`.`Beam_Transv_Reinf` (`Reinf_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Table `element_database_phys`.`Column_Transv_Reinf`
-- -----------------------------------------------------
CREATE TABLE `Column_Transv_Reinf` (
  `Transv_ID` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `Zone_ID` VARCHAR(30) NOT NULL,
  `Reinf_ID` VARCHAR(30) NOT NULL,
  `num_legs` VARCHAR(50) NOT NULL,
  `volumetric_ratio_mm3` VARCHAR(50) NOT NULL,
  PRIMARY KEY (`Transv_ID`),
  -- Link back to the core Column_Transv_Reinf
  CONSTRAINT `fk_phys_transv_to_col_core_transv`
    FOREIGN KEY (`Transv_ID`)
    REFERENCES `element_database_core`.`Column_Transv_Reinf` (`Transv_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  -- Link back to the phys Column_Zone_Geometry via its Zone_ID
  CONSTRAINT `fk_phys_transv_to_col_phys_zone`
    FOREIGN KEY (`Zone_ID`)
    REFERENCES `element_database_phys`.`Column_Zone_Geometry` (`Zone_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  -- Informational link to the overall Reinf_ID
  CONSTRAINT `fk_phys_transv_to_col_core_reinf`
    FOREIGN KEY (`Reinf_ID`)
    REFERENCES `element_database_core`.`Column_Transv_Reinf` (`Reinf_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Table `element_database_phys`.`Slab_Transv_Reinf`
-- -----------------------------------------------------
CREATE TABLE `Slab_Transv_Reinf` (
  `Transv_ID` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `Zone_ID` VARCHAR(30) NOT NULL,
  `Reinf_ID` VARCHAR(30) NOT NULL,
  `num_legs` VARCHAR(50) NOT NULL,
  `volumetric_ratio_mm3` VARCHAR(50) NOT NULL,
  PRIMARY KEY (`Transv_ID`),
  -- Link back to the core Slab_Transv_Reinf
  CONSTRAINT `fk_phys_transv_to_slab_core_transv`
    FOREIGN KEY (`Transv_ID`)
    REFERENCES `element_database_core`.`Slab_Transv_Reinf` (`Transv_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  -- Link back to the phys Slab_Zone_Geometry via its Zone_ID
  CONSTRAINT `fk_phys_transv_to_slab_phys_zone`
    FOREIGN KEY (`Zone_ID`)
    REFERENCES `element_database_phys`.`Slab_Zone_Geometry` (`Zone_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  -- Informational link to the overall Reinf_ID
  CONSTRAINT `fk_phys_transv_to_slab_core_reinf`
    FOREIGN KEY (`Reinf_ID`)
    REFERENCES `element_database_core`.`Slab_Transv_Reinf` (`Reinf_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Table `element_database_phys`.`HCS_Prestressing`
-- -----------------------------------------------------
CREATE TABLE `HCS_Prestressing` (
  `Strand_ID` VARCHAR(45) NOT NULL,
  `Reinf_ID` VARCHAR(30) NOT NULL,
  `tendon_area_mm2` FLOAT NOT NULL,
  `effective_depth_mm` DECIMAL(10,3) NOT NULL,
  PRIMARY KEY (`Strand_ID`),
  -- Link back to the core HCS_Prestressing table
  CONSTRAINT `fk_phys_prestress_to_core_prestress`
    FOREIGN KEY (`Strand_ID`)
    REFERENCES `element_database_core`.`HCS_Prestressing` (`Strand_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  -- Link back to the parent core HCS_Geometry table via the Reinf_ID
  CONSTRAINT `fk_phys_prestress_to_core_geom`
    FOREIGN KEY (`Reinf_ID`)
    REFERENCES `element_database_core`.`HCS_Geometry` (`Reinf_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB;

-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema element_database_core
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema element_database_core
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `element_database_core` DEFAULT CHARACTER SET utf8 ;
USE `element_database_core` ;

-- -----------------------------------------------------
-- Table `element_database_core`.`Donor_Building`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `element_database_core`.`Donor_Building` (
  `Building_ID` VARCHAR(45) NOT NULL,
  `Name` VARCHAR(45) NOT NULL,
  `Building_Type` VARCHAR(45) NOT NULL,
  `Coords_LatLong` POINT NOT NULL,
  `Country` VARCHAR(45) NOT NULL,
  `City` VARCHAR(45) NOT NULL,
  `Construction` YEAR NOT NULL,
  `Deconstruction` YEAR NOT NULL,
  `Deconstruction_Company` VARCHAR(100) NOT NULL,
  `Consequence_Class` VARCHAR(10) NULL,
  `Exposure_Class` VARCHAR(10) NULL,
  `Total_Floor_Area` FLOAT NOT NULL,
  `Num_Wings` INT NOT NULL,
  `Num_Storeys` VARCHAR(45) NOT NULL,
  `Notes` TEXT(65000) NULL,
  UNIQUE INDEX `Name_UNIQUE` (`Name` ASC) VISIBLE,
  PRIMARY KEY (`Building_ID`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `element_database_core`.`Circularity_Data`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `element_database_core`.`Circularity_Data` (
  `Building_ID` VARCHAR(45) NOT NULL,
  `Num_Walls` INT NOT NULL,
  `Num_Columns` INT NOT NULL,
  `Num_Beams` INT NOT NULL,
  `Num_Floor_Slabs` INT NOT NULL,
  `Reclaimed_m3` FLOAT NULL,
  `Recycled_m3` FLOAT NULL,
  `Waste_m3` FLOAT NULL,
  `Material_Circularity_Indicator` FLOAT NULL,
  PRIMARY KEY (`Building_ID`),
  CONSTRAINT `fk_Circularity_Data_Donor_Building`
    FOREIGN KEY (`Building_ID`)
    REFERENCES `element_database_core`.`Donor_Building` (`Building_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `element_database_core`.`Concrete_Props`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `element_database_core`.`Concrete_Props` (
  `Strength_Class` VARCHAR(30) NOT NULL,
  `Original_Standard` VARCHAR(100) NULL,
  `Publication_Year` VARCHAR(45) NOT NULL,
  `Country` VARCHAR(25) NOT NULL,
  `f_ck` FLOAT NULL,
  `f_cm` FLOAT NULL,
  `Measurement_Method` ENUM('Cube', 'Cylinder') NULL,
  `f_ctk` FLOAT NULL,
  `f_ctm` FLOAT NULL,
  `Elastic_Modulus` FLOAT NULL,
  `Ultimate_Strain` FLOAT NULL,
  `Coefficient_Thermal_Exp` FLOAT NULL,
  `Density` FLOAT NULL,
  `Poisson_Ratio` FLOAT NULL,
  `Linked_Resources` VARCHAR(1000) NULL,
  `Notes` TEXT(65000) NULL,
  PRIMARY KEY (`Strength_Class`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `element_database_core`.`Wall_Geometry`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `element_database_core`.`Wall_Geometry` (
  `Product_ID` VARCHAR(30) NOT NULL,
  `Reinf_ID` VARCHAR(30) NULL,
  `Mirrored` TINYINT NOT NULL,
  `Count` INT UNSIGNED NOT NULL,
  `Coords_XYZ` TEXT(65000) NOT NULL,
  `Shell_XYZ` TEXT(65000) NOT NULL,
  `Rad_Bev_XYZ` TEXT(65000) NULL,
  `FootprintPolyline` POLYGON NOT NULL,
  `Strength_Class` VARCHAR(30) NULL,
  `Concrete_Type` ENUM('Normal', 'Lightweight', 'Insulating ultralight', 'UHPC', 'Heavyweight', 'Pervious') NULL,
  `Agg_Size` INT NULL,
  `Files` VARCHAR(1000) NULL,
  `Notes` TEXT(65000) NULL,
  `Has_Void` TINYINT NOT NULL,
  `Has_ExtPanels` TINYINT NOT NULL,
  `Has_Connections` TINYINT NOT NULL,
  `Has_Corbel` TINYINT NOT NULL,
  PRIMARY KEY (`Product_ID`),
  INDEX `FOREIGN` (`Reinf_ID` ASC) VISIBLE,
  INDEX `fk_Wall_Geometry_Concrete_Props1_idx` (`Strength_Class` ASC) VISIBLE,
  CONSTRAINT `fk_Wall_Geometry_Concrete_Props1`
    FOREIGN KEY (`Strength_Class`)
    REFERENCES `element_database_core`.`Concrete_Props` (`Strength_Class`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `element_database_core`.`Element_Super`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `element_database_core`.`Element_Super` (
  `Element_ID` CHAR(36) NOT NULL,
  `Element_Type` ENUM('Wall', 'Beam', 'Column', 'Slab') NOT NULL,
  `Tag_Type` VARCHAR(100) NULL,
  `Tag_IP_Protection` VARCHAR(50) NULL,
  `Tag_Serial_Num` VARCHAR(100) NULL,
  `QR_Code` VARCHAR(1000) NULL,
  PRIMARY KEY (`Element_ID`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `element_database_core`.`Wall_Element`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `element_database_core`.`Wall_Element` (
  `Element_ID` CHAR(36) NOT NULL,
  `Wall_ID` VARCHAR(45) NOT NULL,
  `Building_ID` VARCHAR(45) NOT NULL,
  `CoClass Classifier` JSON NULL,
  `Product_ID` VARCHAR(30) NULL,
  `Reinf_ID` VARCHAR(30) NULL,
  `Wall_Type` VARCHAR(45) NOT NULL,
  `Wing` VARCHAR(30) NOT NULL,
  `Floor_Num` INT NOT NULL,
  `Orientation` VARCHAR(45) NOT NULL,
  `Grid_Pos` VARCHAR(15) NULL,
  `Coating_Protection` TINYINT NULL,
  `QA_Inspection` JSON NULL,
  `Status` ENUM('Active', 'Pending', 'In Use') NOT NULL,
  `Intervention_Class` ENUM('Installation-Ready', 'Maintenance', 'Strengthening') NOT NULL,
  `Location` POINT NOT NULL,
  `File_Links` VARCHAR(1000) NULL,
  `Notes` TEXT(65000) NULL,
  `Has_Tests` TINYINT NOT NULL,
  `Has_Damage` TINYINT NOT NULL,
  UNIQUE INDEX `Wall_ID_UNIQUE` (`Wall_ID` ASC) VISIBLE,
  PRIMARY KEY (`Element_ID`),
  INDEX `Building_ID_fk` (`Building_ID` ASC) VISIBLE,
  INDEX `Prod_ID_fk` (`Product_ID` ASC) VISIBLE,
  CONSTRAINT `fk_Wall_Element_Wall_Geometry1`
    FOREIGN KEY (`Product_ID`)
    REFERENCES `element_database_core`.`Wall_Geometry` (`Product_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Wall_Element_Element_Super1`
    FOREIGN KEY (`Element_ID`)
    REFERENCES `element_database_core`.`Element_Super` (`Element_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `element_database_core`.`Beam_Geometry`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `element_database_core`.`Beam_Geometry` (
  `Product_ID` VARCHAR(30) NOT NULL,
  `Reinf_ID` VARCHAR(30) NULL,
  `Mirrored` TINYINT NOT NULL,
  `Count` INT UNSIGNED NOT NULL,
  `Coords_XYZ` TEXT(65000) NOT NULL,
  `Shell_XYZ` TEXT(65000) NOT NULL,
  `FootprintPolyline` POLYGON NOT NULL,
  `Strength_Class` VARCHAR(30) NULL,
  `Concrete_Type` ENUM('Normal', 'Lightweight', 'Insulating ultralight', 'UHPC', 'Heavyweight', 'Pervious') NULL,
  `Agg_Size` INT NULL,
  `Files` VARCHAR(500) NULL,
  `Notes` TEXT(65000) NULL,
  `Has_Connections` TINYINT NOT NULL,
  `Has_Corbel` TINYINT NOT NULL,
  PRIMARY KEY (`Product_ID`),
  INDEX `FOREIGN` (`Reinf_ID` ASC) VISIBLE,
  INDEX `fk_Beam_Geometry_Concrete_Props1_idx` (`Strength_Class` ASC) VISIBLE,
  CONSTRAINT `fk_Beam_Geometry_Concrete_Props`
    FOREIGN KEY (`Strength_Class`)
    REFERENCES `element_database_core`.`Concrete_Props` (`Strength_Class`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `element_database_core`.`Column_Geometry`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `element_database_core`.`Column_Geometry` (
  `Product_ID` VARCHAR(30) NOT NULL,
  `Reinf_ID` VARCHAR(30) NULL,
  `Cross_Section` ENUM('Rectangular', 'Elliptical') NOT NULL,
  `Count` INT UNSIGNED NOT NULL,
  `Coords_XYZ` TEXT(65000) NOT NULL,
  `Rad_Bev_XYZ` TEXT(65000) NULL,
  `Shell_XYZ` TEXT(65000) NOT NULL,
  `FootprintPolyline` POLYGON NOT NULL,
  `Strength_Class` VARCHAR(30) NULL,
  `Concrete_Type` ENUM('Normal', 'Lightweight', 'Insulating ultralight', 'UHPC', 'Heavyweight', 'Pervious') NULL,
  `Agg_Size` INT NULL,
  `Files` VARCHAR(500) NULL,
  `Notes` TEXT(65000) NULL,
  `Has_Connections` TINYINT NOT NULL,
  `Has_Corbel` TINYINT NOT NULL,
  PRIMARY KEY (`Product_ID`),
  INDEX `FOREIGN` (`Reinf_ID` ASC) VISIBLE,
  INDEX `fk_Column_Geometry_Concrete_Props1_idx` (`Strength_Class` ASC) VISIBLE,
  CONSTRAINT `fk_Column_Geometry_Concrete_Props`
    FOREIGN KEY (`Strength_Class`)
    REFERENCES `element_database_core`.`Concrete_Props` (`Strength_Class`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `element_database_core`.`Corbel_Geometry`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `element_database_core`.`Corbel_Geometry` (
  `Corbel_ID` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `Wall_Product_ID` VARCHAR(30) NULL,
  `Beam_Product_ID` VARCHAR(30) NULL,
  `Column_Product_ID` VARCHAR(30) NULL,
  `Extruded_Plane` ENUM('XZ', 'YZ') NOT NULL,
  `Corb_Coords_XYZ` TEXT(65000) NOT NULL,
  `Corb_Shell_XYZ` TEXT(65000) NOT NULL,
  `Notes` TEXT(65000) NULL,
  PRIMARY KEY (`Corbel_ID`),
  UNIQUE INDEX `Corbel_ID_UNIQUE` (`Corbel_ID` ASC) VISIBLE,
  INDEX `fk_Corbel_Geometry_Wall_Geometry1_idx` (`Wall_Product_ID` ASC) VISIBLE,
  INDEX `fk_Corbel_Geometry_Beam_Geometry1_idx` (`Beam_Product_ID` ASC) VISIBLE,
  INDEX `fk_Corbel_Geometry_Column_Geometry1_idx` (`Column_Product_ID` ASC) VISIBLE,
  CONSTRAINT `fk_Corbel_Geometry_Wall_Geometry1`
    FOREIGN KEY (`Wall_Product_ID`)
    REFERENCES `element_database_core`.`Wall_Geometry` (`Product_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Corbel_Geometry_Beam_Geometry1`
    FOREIGN KEY (`Beam_Product_ID`)
    REFERENCES `element_database_core`.`Beam_Geometry` (`Product_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Corbel_Geometry_Column_Geometry1`
    FOREIGN KEY (`Column_Product_ID`)
    REFERENCES `element_database_core`.`Column_Geometry` (`Product_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `element_database_core`.`Steel_Props`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `element_database_core`.`Steel_Props` (
  `Steel_Grade` VARCHAR(30) NOT NULL,
  `Original_Standard` VARCHAR(100) NULL,
  `Publication_Year` VARCHAR(45) NOT NULL,
  `Country` VARCHAR(30) NOT NULL,
  `f_yk` FLOAT NULL,
  `f_su` FLOAT NULL,
  `Elastic_Modulus` FLOAT NULL,
  `Ultimate_Strain` FLOAT NULL,
  `Fracture_Strain` FLOAT NULL,
  `Measurement_Length` VARCHAR(10) NULL,
  `Delivery` VARCHAR(100) NULL,
  `Ductility_Class` VARCHAR(5) NULL,
  `Surface_Profile` VARCHAR(45) NULL,
  `Coefficient_Thermal_Exp` FLOAT NULL,
  `Linked_Resources` VARCHAR(1000) NULL,
  `Notes` TEXT(65000) NULL,
  PRIMARY KEY (`Steel_Grade`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `element_database_core`.`Wall_Long_Reinf`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `element_database_core`.`Wall_Long_Reinf` (
  `Long_ID` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `Reinf_ID` VARCHAR(30) NOT NULL,
  `Zone_ID` VARCHAR(30) NOT NULL,
  `Zone_Plane` ENUM('XY', 'XZ', 'YZ') NOT NULL,
  `Zone_Coords` POLYGON NOT NULL,
  `Layer_ID` VARCHAR(30) NOT NULL,
  `Layer_Coords` LINESTRING NOT NULL,
  `Layer_Start` INT NOT NULL,
  `Num_Bars` INT NOT NULL,
  `Bar_Diameter` INT NOT NULL,
  `Bar_Spacing` INT NOT NULL,
  `Anchorage_Type` VARCHAR(30) NOT NULL,
  `Steel_Grade` VARCHAR(30) NOT NULL,
  `Cover_Depth` FLOAT NOT NULL,
  `Confidence_Margin` FLOAT NULL,
  `Notes` TEXT(65000) NULL,
  PRIMARY KEY (`Long_ID`),
  INDEX `fk_Wall_Long_Reinf_Wall_Geometry1_idx` (`Reinf_ID` ASC) VISIBLE,
  INDEX `fk_Wall_Long_Reinf_Steel_Props1_idx` (`Steel_Grade` ASC) VISIBLE,
  INDEX `FOREIGN_1` (`Zone_ID` ASC) INVISIBLE,
  INDEX `FOREIGN_2` (`Layer_ID` ASC) VISIBLE,
  CONSTRAINT `fk_Wall_Long_Reinf_Wall_Geometry1`
    FOREIGN KEY (`Reinf_ID`)
    REFERENCES `element_database_core`.`Wall_Geometry` (`Reinf_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Wall_Long_Reinf_Steel_Props1`
    FOREIGN KEY (`Steel_Grade`)
    REFERENCES `element_database_core`.`Steel_Props` (`Steel_Grade`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `element_database_core`.`Wall_Transv_Reinf`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `element_database_core`.`Wall_Transv_Reinf` (
  `Transv_ID` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `Reinf_ID` VARCHAR(30) NOT NULL,
  `Zone_ID` VARCHAR(30) NOT NULL,
  `Description` VARCHAR(50) NOT NULL,
  `Bent_Plane` ENUM('XY', 'XZ', 'YZ') NOT NULL,
  `Num_Bends` INT NOT NULL,
  `Shape_Coords` VARCHAR(500) NOT NULL,
  `Span_Axis` ENUM('X', 'Z', 'Y') NOT NULL,
  `Spanned_Length` VARCHAR(50) NOT NULL,
  `Spacing` FLOAT NOT NULL,
  `Bar_Diameter` INT NOT NULL,
  `Steel_Grade` VARCHAR(30) NOT NULL,
  `Notes` TEXT(65000) NULL,
  PRIMARY KEY (`Transv_ID`),
  INDEX `fk_Wall_Transv_Reinf_Steel_Props1_idx` (`Steel_Grade` ASC) VISIBLE,
  INDEX `fk_Wall_Transv_Reinf_Wall_Long_Reinf1_idx` (`Zone_ID` ASC) VISIBLE,
  INDEX `Wall_Reinf_ID_idx` (`Reinf_ID` ASC) VISIBLE,
  CONSTRAINT `fk_Wall_Transv_Reinf_Steel_Props1`
    FOREIGN KEY (`Steel_Grade`)
    REFERENCES `element_database_core`.`Steel_Props` (`Steel_Grade`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Wall_Transv_Reinf_Wall_Long_Reinf1`
    FOREIGN KEY (`Zone_ID`)
    REFERENCES `element_database_core`.`Wall_Long_Reinf` (`Zone_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `element_database_core`.`Wall_Voids`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `element_database_core`.`Wall_Voids` (
  `Void_ID` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `Product_ID` VARCHAR(30) NOT NULL,
  `Void_Coords_XYZ` TEXT(65000) NOT NULL,
  `Void_Shell_XYZ` TEXT(65000) NOT NULL,
  `Notes` TEXT(65000) NULL,
  PRIMARY KEY (`Void_ID`),
  CONSTRAINT `fk_Wall Voids_Wall_Geometry1`
    FOREIGN KEY (`Product_ID`)
    REFERENCES `element_database_core`.`Wall_Geometry` (`Product_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `element_database_core`.`HCS_Geometry`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `element_database_core`.`HCS_Geometry` (
  `Product_ID` VARCHAR(30) NOT NULL,
  `Reinf_ID` VARCHAR(30) NULL,
  `Count` INT NOT NULL,
  `Height` INT NOT NULL,
  `Length` INT NOT NULL,
  `Width` INT NOT NULL,
  `Voids_Count` INT NOT NULL,
  `Void_Diameter_XY` POINT NOT NULL,
  `Cover_Top` FLOAT NOT NULL,
  `Cover_Bottom` FLOAT NOT NULL,
  `ExtWeb_Thickness` FLOAT NOT NULL,
  `IntWeb_Thickness` FLOAT NOT NULL,
  `Strength_Class` VARCHAR(30) NULL,
  `Density` FLOAT NULL,
  `Agg_Size` INT NULL,
  `Files` VARCHAR(500) NULL,
  `Notes` TEXT(65000) NULL,
  `Has_Topping` TINYINT NOT NULL,
  INDEX `FOREIGN` (`Reinf_ID` ASC) VISIBLE,
  PRIMARY KEY (`Product_ID`),
  INDEX `fk_HCS_Geometry_Concrete_Props1_idx` (`Strength_Class` ASC) VISIBLE,
  CONSTRAINT `fk_HCS_Geometry_Concrete_Props1`
    FOREIGN KEY (`Strength_Class`)
    REFERENCES `element_database_core`.`Concrete_Props` (`Strength_Class`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `element_database_core`.`HCS_Prestressing`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `element_database_core`.`HCS_Prestressing` (
  `Strand_ID` VARCHAR(45) NOT NULL,
  `Reinf_ID` VARCHAR(30) NOT NULL,
  `Layer_Num` INT NOT NULL,
  `Strand_Coord_XY` POINT NOT NULL,
  `Num_Wires` INT NOT NULL,
  `Strand_Diameter` FLOAT NOT NULL,
  `Steel_Grade` VARCHAR(30) NULL,
  `Notes` TEXT(65000) NULL,
  PRIMARY KEY (`Strand_ID`),
  INDEX `fk_HCS_Prestressing_HCS_Geometry1_idx` (`Reinf_ID` ASC) VISIBLE,
  INDEX `fk_HCS_Prestressing_Steel_Props1_idx` (`Steel_Grade` ASC) VISIBLE,
  CONSTRAINT `fk_HCS_Prestressing_HCS_Geometry1`
    FOREIGN KEY (`Reinf_ID`)
    REFERENCES `element_database_core`.`HCS_Geometry` (`Reinf_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_HCS_Prestressing_Steel_Props1`
    FOREIGN KEY (`Steel_Grade`)
    REFERENCES `element_database_core`.`Steel_Props` (`Steel_Grade`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `element_database_core`.`Beam_Element`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `element_database_core`.`Beam_Element` (
  `Element_ID` CHAR(36) NOT NULL,
  `Beam_ID` VARCHAR(45) NOT NULL,
  `Building_ID` VARCHAR(45) NOT NULL,
  `CoClass Classifier` JSON NULL,
  `Product_ID` VARCHAR(30) NULL,
  `Reinf_ID` VARCHAR(30) NULL,
  `Beam_Type` VARCHAR(45) NOT NULL,
  `Wing` VARCHAR(30) NOT NULL,
  `Floor_Num` INT NOT NULL,
  `Grid_Pos` VARCHAR(15) NULL,
  `Coating_Protection` TINYINT NULL,
  `QA_Inspection` JSON NULL,
  `Status` ENUM('Active', 'Pending', 'In Use') NOT NULL,
  `Intervention_Class` ENUM('Installation-Ready', 'Maintenance', 'Strengthening') NOT NULL,
  `Location` POINT NOT NULL,
  `File_Links` VARCHAR(1000) NULL,
  `Notes` TEXT(65000) NULL,
  `Has_Tests` TINYINT NOT NULL,
  `Has_Damage` TINYINT NOT NULL,
  PRIMARY KEY (`Element_ID`),
  UNIQUE INDEX `Beam_ID_UNIQUE` (`Beam_ID` ASC) VISIBLE,
  INDEX `Building_ID_fk` (`Building_ID` ASC) VISIBLE,
  INDEX `Prod_ID_fk` (`Product_ID` ASC) VISIBLE,
  CONSTRAINT `fk_Beam_Element_Beam_Geometry1`
    FOREIGN KEY (`Product_ID`)
    REFERENCES `element_database_core`.`Beam_Geometry` (`Product_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Beam_Element_Element_Super1`
    FOREIGN KEY (`Element_ID`)
    REFERENCES `element_database_core`.`Element_Super` (`Element_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `element_database_core`.`Column_Element`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `element_database_core`.`Column_Element` (
  `Element_ID` CHAR(36) NOT NULL,
  `Column_ID` VARCHAR(45) NOT NULL,
  `Building_ID` VARCHAR(45) NOT NULL,
  `CoClass Classifier` JSON NULL,
  `Product_ID` VARCHAR(30) NULL,
  `Reinf_ID` VARCHAR(30) NULL,
  `Column_Type` VARCHAR(45) NOT NULL,
  `Wing` VARCHAR(30) NOT NULL,
  `Floor_Num` INT NOT NULL,
  `Grid_Pos` VARCHAR(15) NULL,
  `Coating_Protection` TINYINT NULL,
  `QA_Inspection` JSON NULL,
  `Status` ENUM('Active', 'Pending', 'In Use') NOT NULL,
  `Intervention_Class` ENUM('Installation-Ready', 'Maintenance', 'Strengthening') NOT NULL,
  `Location` POINT NOT NULL,
  `File_Links` VARCHAR(1000) NULL,
  `Notes` TEXT(65000) NULL,
  `Has_Tests` TINYINT NOT NULL,
  `Has_Damage` TINYINT NOT NULL,
  PRIMARY KEY (`Element_ID`),
  UNIQUE INDEX `Column_ID_UNIQUE` (`Column_ID` ASC) VISIBLE,
  INDEX `Building_ID_fk` (`Building_ID` ASC) VISIBLE,
  INDEX `Prod_ID_fk` (`Product_ID` ASC) VISIBLE,
  CONSTRAINT `fk_Column_Element_Column_Geometry1`
    FOREIGN KEY (`Product_ID`)
    REFERENCES `element_database_core`.`Column_Geometry` (`Product_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Column_Element_Element_Super1`
    FOREIGN KEY (`Element_ID`)
    REFERENCES `element_database_core`.`Element_Super` (`Element_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `element_database_core`.`Slab_Geometry`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `element_database_core`.`Slab_Geometry` (
  `Product_ID` VARCHAR(30) NOT NULL,
  `Reinf_ID` VARCHAR(30) NULL,
  `Count` INT UNSIGNED NOT NULL,
  `Coords_XYZ` TEXT(65000) NOT NULL,
  `Shell_XYZ` TEXT(65000) NOT NULL,
  `FootprintPolyline` POLYGON NOT NULL,
  `Strength_Class` VARCHAR(30) NULL,
  `Concrete_Type` ENUM('Normal', 'Lightweight', 'Insulating ultralight', 'UHPC', 'Heavyweight', 'Pervious') NULL,
  `Agg_Size` INT NULL,
  `Files` VARCHAR(500) NULL,
  `Notes` TEXT(65000) NULL,
  `Has_Connections` TINYINT NOT NULL,
  `Has_Void` TINYINT NOT NULL,
  PRIMARY KEY (`Product_ID`),
  INDEX `FOREIGN` (`Reinf_ID` ASC) VISIBLE,
  INDEX `fk_Slab_Geometry_Concrete_Props1_idx` (`Strength_Class` ASC) VISIBLE,
  CONSTRAINT `fk_Slab_Geometry_Concrete_Props`
    FOREIGN KEY (`Strength_Class`)
    REFERENCES `element_database_core`.`Concrete_Props` (`Strength_Class`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `element_database_core`.`Slab_Element`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `element_database_core`.`Slab_Element` (
  `Element_ID` CHAR(36) NOT NULL,
  `Slab_ID` VARCHAR(45) NOT NULL,
  `Building_ID` VARCHAR(45) NOT NULL,
  `CoClass Classifier` JSON NULL,
  `Slab_Product_ID` VARCHAR(30) NULL,
  `HCS_Product_ID` VARCHAR(30) NULL,
  `Reinf_ID` VARCHAR(30) NULL,
  `Slab_Type` VARCHAR(45) NOT NULL,
  `Wing` VARCHAR(30) NOT NULL,
  `Floor_Num` INT NOT NULL,
  `Grid_Pos` VARCHAR(45) NULL,
  `Coating_Protection` TINYINT NULL,
  `QA_Inspection` JSON NULL,
  `Status` ENUM('Active', 'Pending', 'In Use') NOT NULL,
  `Intervention_Class` ENUM('Installation-Ready', 'Maintenance', 'Strengthening') NOT NULL,
  `Location` POINT NOT NULL,
  `File_Links` VARCHAR(1000) NULL,
  `Notes` TEXT(65000) NULL,
  `Has_Tests` TINYINT NOT NULL,
  `Has_Damage` TINYINT NOT NULL,
  PRIMARY KEY (`Element_ID`),
  UNIQUE INDEX `Slab_ID_UNIQUE` (`Slab_ID` ASC) VISIBLE,
  INDEX `Building_ID_fk` (`Building_ID` ASC) VISIBLE,
  INDEX `fk_Slab_Element_Slab_Geometry1_idx` (`Slab_Product_ID` ASC) VISIBLE,
  INDEX `fk_Slab_Element_HCS_Geometry1_idx` (`HCS_Product_ID` ASC) VISIBLE,
  CONSTRAINT `fk_Slab_Element_Slab_Geometry1`
    FOREIGN KEY (`Slab_Product_ID`)
    REFERENCES `element_database_core`.`Slab_Geometry` (`Product_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Slab_Element_HCS_Geometry1`
    FOREIGN KEY (`HCS_Product_ID`)
    REFERENCES `element_database_core`.`HCS_Geometry` (`Product_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Slab_Element_Element_Super1`
    FOREIGN KEY (`Element_ID`)
    REFERENCES `element_database_core`.`Element_Super` (`Element_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `element_database_core`.`Additional_Panelling`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `element_database_core`.`Additional_Panelling` (
  `Product_ID` VARCHAR(30) NOT NULL,
  `Has_Void` TINYINT NOT NULL,
  `Panel_Coords_XYZ` TEXT(65000) NULL,
  `Panel_Shell_XYZ` TEXT(65000) NULL,
  `Rad_Bev_XYZ` TEXT(65000) NULL,
  `Design_Finish` VARCHAR(45) NULL,
  `Insul_Coords_XYZ` TEXT(65000) NULL,
  `Insul_Shell_XYZ` TEXT(65000) NULL,
  `Notes` TEXT(65000) NULL,
  `Links` VARCHAR(1000) NULL,
  PRIMARY KEY (`Product_ID`),
  CONSTRAINT `fk_Additional_Panelling_Wall_Geometry1`
    FOREIGN KEY (`Product_ID`)
    REFERENCES `element_database_core`.`Wall_Geometry` (`Product_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `element_database_core`.`Wall_Connections`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `element_database_core`.`Wall_Connections` (
  `Connection_ID` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `Product_ID` VARCHAR(30) NOT NULL,
  `Connection_Type` VARCHAR(45) NOT NULL,
  `Position_XYZ` VARCHAR(500) NOT NULL,
  `Depth` FLOAT NOT NULL,
  `Diameter` FLOAT NOT NULL,
  `Notes` TEXT(65000) NULL,
  PRIMARY KEY (`Connection_ID`),
  UNIQUE INDEX `Connection_ID_UNIQUE` (`Connection_ID` ASC) VISIBLE,
  CONSTRAINT `fk_Wall_Connections_Wall_Geometry1`
    FOREIGN KEY (`Product_ID`)
    REFERENCES `element_database_core`.`Wall_Geometry` (`Product_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `element_database_core`.`Beam_Long_Reinf`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `element_database_core`.`Beam_Long_Reinf` (
  `Long_ID` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `Reinf_ID` VARCHAR(30) NOT NULL,
  `Zone_ID` VARCHAR(30) NOT NULL,
  `Zone_Plane` ENUM('XY', 'XZ', 'YZ') NOT NULL,
  `Zone_Coords` POLYGON NOT NULL,
  `Layer_ID` VARCHAR(30) NOT NULL,
  `Layer_Coords` LINESTRING NOT NULL,
  `Layer_Start` INT NOT NULL,
  `Num_Bars` INT NOT NULL,
  `Bar_Diameter` INT NOT NULL,
  `Bar_Spacing` INT NOT NULL,
  `Anchorage_Type` VARCHAR(30) NOT NULL,
  `Steel_Grade` VARCHAR(30) NOT NULL,
  `Cover_Depth` FLOAT NOT NULL,
  `Confidence_Margin` FLOAT NULL,
  `Notes` TEXT(65000) NULL,
  PRIMARY KEY (`Long_ID`),
  INDEX `fk_Beam_Long_Reinf_Beam_Geometry1_idx` (`Reinf_ID` ASC) VISIBLE,
  INDEX `fk_Beam_Long_Reinf_Steel_Props1_idx` (`Steel_Grade` ASC) VISIBLE,
  INDEX `FOREIGN_1` (`Zone_ID` ASC) VISIBLE,
  INDEX `FOREIGN_2` (`Layer_ID` ASC) VISIBLE,
  CONSTRAINT `fk_Beam_Long_Reinf_Beam_Geometry`
    FOREIGN KEY (`Reinf_ID`)
    REFERENCES `element_database_core`.`Beam_Geometry` (`Reinf_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Beam_Long_Reinf_Steel_Props`
    FOREIGN KEY (`Steel_Grade`)
    REFERENCES `element_database_core`.`Steel_Props` (`Steel_Grade`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `element_database_core`.`Beam_Transv_Reinf`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `element_database_core`.`Beam_Transv_Reinf` (
  `Transv_ID` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `Reinf_ID` VARCHAR(30) NOT NULL,
  `Zone_ID` VARCHAR(30) NOT NULL,
  `Description` VARCHAR(50) NOT NULL,
  `Bent_Plane` ENUM('XY', 'XZ', 'YZ') NOT NULL,
  `Num_Bends` INT NOT NULL,
  `Shape_Coords` VARCHAR(500) NOT NULL,
  `Span_Axis` ENUM('X', 'Z', 'Y') NOT NULL,
  `Spanned_Length` VARCHAR(50) NOT NULL,
  `Spacing` FLOAT NOT NULL,
  `Bar_Diameter` INT NOT NULL,
  `Steel_Grade` VARCHAR(30) NOT NULL,
  `Notes` TEXT(65000) NULL,
  PRIMARY KEY (`Transv_ID`),
  INDEX `fk_Beam_Transv_Reinf_Steel_Props1_idx` (`Steel_Grade` ASC) VISIBLE,
  INDEX `fk_Beam_Transv_Reinf_Beam_Long_Reinf1_idx` (`Zone_ID` ASC) VISIBLE,
  UNIQUE INDEX `Zone_ID_UNIQUE` (`Zone_ID` ASC) VISIBLE,
  INDEX `Beam_Reinf_ID_idx` (`Reinf_ID` ASC) VISIBLE,
  CONSTRAINT `fk_Beam_Transv_Reinf_Steel_Props10`
    FOREIGN KEY (`Steel_Grade`)
    REFERENCES `element_database_core`.`Steel_Props` (`Steel_Grade`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Beam_Transv_Reinf_Beam_Long_Reinf1`
    FOREIGN KEY (`Zone_ID`)
    REFERENCES `element_database_core`.`Beam_Long_Reinf` (`Zone_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `element_database_core`.`Beam_Connections`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `element_database_core`.`Beam_Connections` (
  `Connection_ID` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `Product_ID` VARCHAR(30) NOT NULL,
  `Connection_Type` VARCHAR(45) NOT NULL,
  `Position_XYZ` VARCHAR(500) NOT NULL,
  `Depth` FLOAT NOT NULL,
  `Diameter` FLOAT NOT NULL,
  `Notes` TEXT(65000) NULL,
  PRIMARY KEY (`Connection_ID`),
  UNIQUE INDEX `Connection_ID_UNIQUE` (`Connection_ID` ASC) VISIBLE,
  CONSTRAINT `fk_Beam_Connections_Beam_Geometry10`
    FOREIGN KEY (`Product_ID`)
    REFERENCES `element_database_core`.`Beam_Geometry` (`Product_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `element_database_core`.`Column_Connections`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `element_database_core`.`Column_Connections` (
  `Connection_ID` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `Product_ID` VARCHAR(30) NOT NULL,
  `Connection_Type` VARCHAR(45) NOT NULL,
  `Position_XYZ` VARCHAR(500) NOT NULL,
  `Depth` FLOAT NOT NULL,
  `Diameter` FLOAT NOT NULL,
  `Notes` TEXT(65000) NULL,
  PRIMARY KEY (`Connection_ID`),
  UNIQUE INDEX `Connection_ID_UNIQUE` (`Connection_ID` ASC) VISIBLE,
  CONSTRAINT `fk_Column_Connections_Column_Geometry`
    FOREIGN KEY (`Product_ID`)
    REFERENCES `element_database_core`.`Column_Geometry` (`Product_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `element_database_core`.`Column_Long_Reinf`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `element_database_core`.`Column_Long_Reinf` (
  `Long_ID` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `Reinf_ID` VARCHAR(30) NOT NULL,
  `Zone_ID` VARCHAR(30) NOT NULL,
  `Zone_Plane` ENUM('XY', 'XZ', 'YZ') NOT NULL,
  `Zone_Coords` POLYGON NOT NULL,
  `Layer_ID` VARCHAR(30) NOT NULL,
  `Layer_Coords` LINESTRING NOT NULL,
  `Layer_Start` INT NOT NULL,
  `Num_Bars` INT NOT NULL,
  `Bar_Diameter` INT NOT NULL,
  `Bar_Spacing` INT NOT NULL,
  `Anchorage_Type` VARCHAR(30) NOT NULL,
  `Steel_Grade` VARCHAR(30) NOT NULL,
  `Cover_Depth` FLOAT NOT NULL,
  `Confidence_Margin` FLOAT NULL,
  `Notes` TEXT(65000) NULL,
  PRIMARY KEY (`Long_ID`),
  INDEX `fk_Column_Long_Reinf_Column_Geometry1_idx` (`Reinf_ID` ASC) INVISIBLE,
  INDEX `fk_Column_Long_Reinf_Steel_Props1_idx` (`Steel_Grade` ASC) INVISIBLE,
  INDEX `FOREIGN_1` (`Zone_ID` ASC) VISIBLE,
  INDEX `FOREIGN_2` (`Layer_ID` ASC) VISIBLE,
  CONSTRAINT `fk_Column_Long_Reinf_Column_Geometry`
    FOREIGN KEY (`Reinf_ID`)
    REFERENCES `element_database_core`.`Column_Geometry` (`Reinf_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Column_Long_Reinf_Steel_Props`
    FOREIGN KEY (`Steel_Grade`)
    REFERENCES `element_database_core`.`Steel_Props` (`Steel_Grade`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `element_database_core`.`Column_Transv_Reinf`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `element_database_core`.`Column_Transv_Reinf` (
  `Transv_ID` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `Reinf_ID` VARCHAR(30) NOT NULL,
  `Zone_ID` VARCHAR(30) NOT NULL,
  `Description` VARCHAR(50) NOT NULL,
  `Bent_Plane` ENUM('XY', 'XZ', 'YZ') NOT NULL,
  `Num_Bends` INT NOT NULL,
  `Shape_Coords` VARCHAR(500) NULL,
  `Elliptical_Shape_Coords` VARCHAR(500) NULL,
  `Span_Axis` ENUM('X', 'Z', 'Y') NOT NULL,
  `Spanned_Length` VARCHAR(50) NOT NULL,
  `Spacing` FLOAT NOT NULL,
  `Bar_Diameter` INT NOT NULL,
  `Steel_Grade` VARCHAR(30) NOT NULL,
  `Notes` TEXT(65000) NULL,
  PRIMARY KEY (`Transv_ID`),
  INDEX `fk_Column_Transv_Reinf_Steel_Props1_idx` (`Steel_Grade` ASC) VISIBLE,
  INDEX `fk_Column_Transv_Reinf_Column_Long_Reinf1_idx` (`Zone_ID` ASC) VISIBLE,
  UNIQUE INDEX `Zone_ID_UNIQUE` (`Zone_ID` ASC) VISIBLE,
  INDEX `Column_Reinf_ID_idx` (`Reinf_ID` ASC) VISIBLE,
  CONSTRAINT `fk_Column_Transv_Reinf_Steel_Props100`
    FOREIGN KEY (`Steel_Grade`)
    REFERENCES `element_database_core`.`Steel_Props` (`Steel_Grade`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Column_Transv_Reinf_Column_Long_Reinf1`
    FOREIGN KEY (`Zone_ID`)
    REFERENCES `element_database_core`.`Column_Long_Reinf` (`Zone_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `element_database_core`.`Slab_Long_Reinf`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `element_database_core`.`Slab_Long_Reinf` (
  `Long_ID` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `Reinf_ID` VARCHAR(30) NOT NULL,
  `Zone_ID` VARCHAR(30) NOT NULL,
  `Zone_Plane` ENUM('XY', 'XZ', 'YZ') NOT NULL,
  `Zone_Coords` POLYGON NOT NULL,
  `Layer_ID` VARCHAR(30) NOT NULL,
  `Layer_Coords` LINESTRING NOT NULL,
  `Layer_Start` INT NOT NULL,
  `Num_Bars` INT NOT NULL,
  `Bar_Diameter` INT NOT NULL,
  `Bar_Spacing` INT NOT NULL,
  `Anchorage_Type` VARCHAR(30) NOT NULL,
  `Steel_Grade` VARCHAR(30) NOT NULL,
  `Cover_Depth` FLOAT NOT NULL,
  `Confidence_Margin` FLOAT NULL,
  `Notes` TEXT(65000) NULL,
  PRIMARY KEY (`Long_ID`),
  INDEX `fk_Slab_Long_Reinf_Slab_Geometry1_idx` (`Reinf_ID` ASC) VISIBLE,
  INDEX `FOREIGN_1` (`Zone_ID` ASC) VISIBLE,
  INDEX `FOREIGN_2` (`Layer_ID` ASC) VISIBLE,
  INDEX `fk_Slab_Long_Reinf_Steel_Props1_idx` (`Steel_Grade` ASC) VISIBLE,
  CONSTRAINT `fk_Slab_Long_Reinf_Slab_Geometry`
    FOREIGN KEY (`Reinf_ID`)
    REFERENCES `element_database_core`.`Slab_Geometry` (`Reinf_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Slab_Long_Reinf_Steel_Props1`
    FOREIGN KEY (`Steel_Grade`)
    REFERENCES `element_database_core`.`Steel_Props` (`Steel_Grade`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `element_database_core`.`Slab_Transv_Reinf`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `element_database_core`.`Slab_Transv_Reinf` (
  `Transv_ID` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `Reinf_ID` VARCHAR(30) NOT NULL,
  `Zone_ID` VARCHAR(30) NOT NULL,
  `Description` VARCHAR(50) NOT NULL,
  `Bent_Plane` ENUM('XY', 'XZ', 'YZ') NOT NULL,
  `Num_Bends` INT NOT NULL,
  `Shape_Coords` VARCHAR(500) NOT NULL,
  `Span_Axis` ENUM('X', 'Z', 'Y') NOT NULL,
  `Spanned_Length` VARCHAR(50) NOT NULL,
  `Spacing` FLOAT NOT NULL,
  `Bar_Diameter` INT NOT NULL,
  `Steel_Grade` VARCHAR(30) NOT NULL,
  `Notes` TEXT(65000) NULL,
  PRIMARY KEY (`Transv_ID`),
  INDEX `fk_Slab_Transv_Reinf_Slab_Long_Reinf1_idx` (`Zone_ID` ASC) VISIBLE,
  UNIQUE INDEX `Zone_ID_UNIQUE` (`Zone_ID` ASC) VISIBLE,
  INDEX `Slab_Reinf_ID_idx` (`Reinf_ID` ASC) VISIBLE,
  INDEX `fk_Slab_Transv_Reinf_Steel_Props1_idx` (`Steel_Grade` ASC) VISIBLE,
  CONSTRAINT `fk_Slab_Transv_Reinf_Slab_Long_Reinf1`
    FOREIGN KEY (`Zone_ID`)
    REFERENCES `element_database_core`.`Slab_Long_Reinf` (`Zone_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Slab_Transv_Reinf_Steel_Props1`
    FOREIGN KEY (`Steel_Grade`)
    REFERENCES `element_database_core`.`Steel_Props` (`Steel_Grade`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `element_database_core`.`Slab_Connections`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `element_database_core`.`Slab_Connections` (
  `Connection_ID` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `Product_ID` VARCHAR(30) NOT NULL,
  `Connection_Type` VARCHAR(45) NOT NULL,
  `Position_XYZ` VARCHAR(500) NOT NULL,
  `Depth` FLOAT NOT NULL,
  `Diameter` FLOAT NOT NULL,
  `Notes` TEXT(65000) NULL,
  PRIMARY KEY (`Connection_ID`),
  UNIQUE INDEX `Connection_ID_UNIQUE` (`Connection_ID` ASC) VISIBLE,
  CONSTRAINT `fk_Slab_Connections_Slab_Geometry1000`
    FOREIGN KEY (`Product_ID`)
    REFERENCES `element_database_core`.`Slab_Geometry` (`Product_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `element_database_core`.`Slab_Voids`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `element_database_core`.`Slab_Voids` (
  `Void_ID` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `Product_ID` VARCHAR(30) NOT NULL,
  `Void_Coords_XYZ` VARCHAR(500) NOT NULL,
  `Void_Shell_XYZ` TEXT(65000) NOT NULL,
  `Notes` TEXT(65000) NULL,
  PRIMARY KEY (`Void_ID`),
  UNIQUE INDEX `Void_ID_UNIQUE` (`Void_ID` ASC) VISIBLE,
  INDEX `fk_Slab_Voids_Slab_Geometry1_idx` (`Product_ID` ASC) VISIBLE,
  CONSTRAINT `fk_Slab_Voids_Slab_Geometry1`
    FOREIGN KEY (`Product_ID`)
    REFERENCES `element_database_core`.`Slab_Geometry` (`Product_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `element_database_core`.`Zone_Anchorage`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `element_database_core`.`Zone_Anchorage` (
  `Anchorage_ID` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `Wall_Zone_ID` VARCHAR(30) NULL,
  `Beam_Zone_ID` VARCHAR(30) NULL,
  `Column_Zone_ID` VARCHAR(30) NULL,
  `Slab_Zone_ID` VARCHAR(30) NULL,
  `Anchorage_Type` VARCHAR(30) NOT NULL,
  `Bent_Angle` VARCHAR(100) NOT NULL,
  `Diameter` INT NOT NULL,
  `Spacing` FLOAT NOT NULL,
  `Num_Pins` INT NOT NULL,
  `Span` ENUM('X', 'Y', 'Z') NOT NULL,
  `Notes` TEXT(65000) NULL,
  PRIMARY KEY (`Anchorage_ID`),
  INDEX `fk_Zone_Anchorage_Wall_Long_Reinf1_idx` (`Wall_Zone_ID` ASC) VISIBLE,
  INDEX `fk_Zone_Anchorage_Beam_Long_Reinf1_idx` (`Beam_Zone_ID` ASC) VISIBLE,
  INDEX `fk_Zone_Anchorage_Column_Long_Reinf1_idx` (`Column_Zone_ID` ASC) VISIBLE,
  INDEX `fk_Zone_Anchorage_Slab_Long_Reinf1_idx` (`Slab_Zone_ID` ASC) VISIBLE,
  CONSTRAINT `fk_Zone_Anchorage_Wall_Long_Reinf1`
    FOREIGN KEY (`Wall_Zone_ID`)
    REFERENCES `element_database_core`.`Wall_Long_Reinf` (`Zone_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Zone_Anchorage_Beam_Long_Reinf1`
    FOREIGN KEY (`Beam_Zone_ID`)
    REFERENCES `element_database_core`.`Beam_Long_Reinf` (`Zone_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Zone_Anchorage_Column_Long_Reinf1`
    FOREIGN KEY (`Column_Zone_ID`)
    REFERENCES `element_database_core`.`Column_Long_Reinf` (`Zone_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Zone_Anchorage_Slab_Long_Reinf1`
    FOREIGN KEY (`Slab_Zone_ID`)
    REFERENCES `element_database_core`.`Slab_Long_Reinf` (`Zone_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `element_database_core`.`Layer_Anchorage`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `element_database_core`.`Layer_Anchorage` (
  `Anchorage_ID` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `Wall_Layer_ID` VARCHAR(30) NULL,
  `Beam_Layer_ID` VARCHAR(30) NULL,
  `Column_Layer_ID` VARCHAR(30) NULL,
  `Slab_Layer_ID` VARCHAR(30) NULL,
  `Anchorage_Type` VARCHAR(30) NOT NULL,
  `Anchor_Start` VARCHAR(100) NOT NULL,
  `Anchor_End` VARCHAR(100) NOT NULL,
  `Notes` TEXT(65000) NULL,
  PRIMARY KEY (`Anchorage_ID`),
  INDEX `fk_Layer_Anchorage_Wall_Long_Reinf1_idx` (`Wall_Layer_ID` ASC) VISIBLE,
  INDEX `fk_Layer_Anchorage_Beam_Long_Reinf1_idx` (`Beam_Layer_ID` ASC) VISIBLE,
  INDEX `fk_Layer_Anchorage_Column_Long_Reinf1_idx` (`Column_Layer_ID` ASC) VISIBLE,
  INDEX `fk_Layer_Anchorage_Slab_Long_Reinf1_idx` (`Slab_Layer_ID` ASC) VISIBLE,
  CONSTRAINT `fk_Layer_Anchorage_Wall_Long_Reinf1`
    FOREIGN KEY (`Wall_Layer_ID`)
    REFERENCES `element_database_core`.`Wall_Long_Reinf` (`Layer_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Layer_Anchorage_Beam_Long_Reinf1`
    FOREIGN KEY (`Beam_Layer_ID`)
    REFERENCES `element_database_core`.`Beam_Long_Reinf` (`Layer_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Layer_Anchorage_Column_Long_Reinf1`
    FOREIGN KEY (`Column_Layer_ID`)
    REFERENCES `element_database_core`.`Column_Long_Reinf` (`Layer_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Layer_Anchorage_Slab_Long_Reinf1`
    FOREIGN KEY (`Slab_Layer_ID`)
    REFERENCES `element_database_core`.`Slab_Long_Reinf` (`Layer_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `element_database_core`.`Structural_Topping`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `element_database_core`.`Structural_Topping` (
  `Product_ID` VARCHAR(30) NOT NULL,
  `Thickness` INT NOT NULL,
  `Mesh_Diameter` INT NOT NULL,
  `Mesh_Spacing` INT NOT NULL,
  `Notes` TEXT(65000) NULL,
  PRIMARY KEY (`Product_ID`),
  CONSTRAINT `fk_Structural Topping_HCS_Geometry1`
    FOREIGN KEY (`Product_ID`)
    REFERENCES `element_database_core`.`HCS_Geometry` (`Product_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `element_database_core`.`HCS_Connections`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `element_database_core`.`HCS_Connections` (
  `Product_ID` VARCHAR(30) NOT NULL,
  `Reinf_ID` VARCHAR(30) NOT NULL,
  `Shear_to_Wall` INT NOT NULL,
  `Position_SW` VARCHAR(500) NOT NULL,
  `Longitudinal_to_Wall` INT NOT NULL,
  `Position_LW` VARCHAR(500) NOT NULL,
  `Shear_to_Slab` INT NOT NULL,
  `Position_SS` VARCHAR(500) NOT NULL,
  `Notes` TEXT(65000) NULL,
  PRIMARY KEY (`Product_ID`),
  CONSTRAINT `fk_HCS_Connections_HCS_Geometry1`
    FOREIGN KEY (`Product_ID`)
    REFERENCES `element_database_core`.`HCS_Geometry` (`Product_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `element_database_core`.`Owner`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `element_database_core`.`Owner` (
  `Owner_ID` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `Name` VARCHAR(100) NOT NULL,
  `Phone` VARCHAR(20) NULL,
  `Email` VARCHAR(100) NULL,
  `Website_URL` VARCHAR(1000) NULL,
  PRIMARY KEY (`Owner_ID`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `element_database_core`.`QC_and_History`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `element_database_core`.`QC_and_History` (
  `Element_ID` CHAR(36) NOT NULL,
  `Building_ID` VARCHAR(45) NOT NULL,
  `Owner_ID` INT UNSIGNED NOT NULL,
  `Service_Life_Num` INT NOT NULL,
  `Service_Start` DATE NULL,
  `Storage_Exposure_Class` VARCHAR(50) NULL,
  `File_Name` VARCHAR(255) NULL,
  `File_Location` VARCHAR(1000) NULL,
  `Uploaded_At` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`Element_ID`, `Building_ID`),
  INDEX `fk_Service_History_Donor_Building1_idx` (`Building_ID` ASC) VISIBLE,
  INDEX `fk_Service_History_Owner1_idx` (`Owner_ID` ASC) VISIBLE,
  CONSTRAINT `fk_Service_History_Donor_Building1`
    FOREIGN KEY (`Building_ID`)
    REFERENCES `element_database_core`.`Donor_Building` (`Building_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Service_History_Element_Super1`
    FOREIGN KEY (`Element_ID`)
    REFERENCES `element_database_core`.`Element_Super` (`Element_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Service_History_Owner1`
    FOREIGN KEY (`Owner_ID`)
    REFERENCES `element_database_core`.`Owner` (`Owner_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `element_database_core`.`Building_Resources`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `element_database_core`.`Building_Resources` (
  `Resource_ID` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `Building_ID` VARCHAR(45) NOT NULL,
  `Resource_Type` ENUM('Drawing', 'Doc', 'BIM', 'PointCloud', 'Scan_Image') NOT NULL,
  `File_Name` VARCHAR(255) NOT NULL,
  `File_Format` VARCHAR(50) NULL,
  `File_Location` VARCHAR(1000) NULL,
  `Metadata` JSON NULL,
  `Uploaded_At` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`Resource_ID`),
  INDEX `fk_Donor_Building_Resources_Donor_Building1_idx` (`Building_ID` ASC) VISIBLE,
  CONSTRAINT `fk_Donor_Building_Resources_Donor_Building1`
    FOREIGN KEY (`Building_ID`)
    REFERENCES `element_database_core`.`Donor_Building` (`Building_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `element_database_core`.`Test_Region`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `element_database_core`.`Test_Region` (
  `Test_Region_ID` INT UNSIGNED NOT NULL,
  `Element_ID` CHAR(36) NOT NULL,
  `Element_Type` ENUM('Wall', 'Beam', 'Column', 'Slab') NOT NULL,
  `Num_Elements` VARCHAR(45) NOT NULL,
  `TR_Volume_m3` FLOAT NOT NULL,
  `Ave_Tests_Per_Elmt` FLOAT NOT NULL,
  PRIMARY KEY (`Test_Region_ID`, `Element_ID`),
  INDEX `fk_TR_Element_Element_Super1_idx` (`Element_ID` ASC) INVISIBLE,
  CONSTRAINT `fk_TR_Element_Element_Super1`
    FOREIGN KEY (`Element_ID`)
    REFERENCES `element_database_core`.`Element_Super` (`Element_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `element_database_core`.`Durability_Assessment`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `element_database_core`.`Durability_Assessment` (
  `Test_Region_ID` INT UNSIGNED NOT NULL,
  `Element_ID` CHAR(36) NOT NULL,
  `Material_Age` YEAR NULL,
  `Cover_Depth` FLOAT NULL,
  `Electrical_Resistivity` FLOAT NULL,
  `Permeability` FLOAT NULL,
  `Ave_Carbonation_Depth` FLOAT NULL,
  `Max_Carbonation_Depth` FLOAT NULL,
  `Corrosion_Rate` FLOAT NULL,
  `Remaining_Init_Time` YEAR NULL,
  `Propagation_Time` YEAR NULL,
  PRIMARY KEY (`Test_Region_ID`, `Element_ID`),
  CONSTRAINT `fk_Durability_Assessment_Test_Region1`
    FOREIGN KEY (`Test_Region_ID` , `Element_ID`)
    REFERENCES `element_database_core`.`Test_Region` (`Test_Region_ID` , `Element_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `element_database_core`.`Concrete_Testing`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `element_database_core`.`Concrete_Testing` (
  `Test_Region_ID` INT UNSIGNED NOT NULL,
  `Element_ID` CHAR(36) NOT NULL,
  `Sample_Size` INT NOT NULL,
  `Drilling_Orientation` ENUM('H', 'V') NOT NULL,
  `Core_Height` FLOAT NOT NULL,
  `Core_Diameter` FLOAT NOT NULL,
  `fcm` FLOAT NOT NULL,
  `fc_Std_Dev` FLOAT NOT NULL,
  `fck` FLOAT NOT NULL,
  `Equiv_EC_Class` VARCHAR(10) NOT NULL,
  `ftm` FLOAT NULL,
  `ft_Std_Dev` FLOAT NULL,
  `Elastic_Modulus` FLOAT NULL,
  `Ult_Strain` FLOAT NULL,
  `Max_Agg_Size` FLOAT NULL,
  `W/C_Ratio` FLOAT NULL,
  `Air_Content` FLOAT NULL,
  `Density` FLOAT NULL,
  `Notes` TEXT NULL,
  PRIMARY KEY (`Test_Region_ID`, `Element_ID`),
  INDEX `fk_Concrete_Testing_Test_Region1_idx` (`Element_ID` ASC, `Test_Region_ID` ASC) VISIBLE,
  CONSTRAINT `fk_Concrete_Testing_Test_Region1`
    FOREIGN KEY (`Element_ID` , `Test_Region_ID`)
    REFERENCES `element_database_core`.`Test_Region` (`Element_ID` , `Test_Region_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `element_database_core`.`Reinforcement_Testing`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `element_database_core`.`Reinforcement_Testing` (
  `Test_Region_ID` INT UNSIGNED NOT NULL,
  `Element_ID` CHAR(36) NOT NULL,
  `Gauge_Length` FLOAT NOT NULL,
  `Sample_Size` INT NOT NULL,
  `Sample_Diameter` FLOAT NOT NULL,
  `fym` FLOAT NOT NULL,
  `fy_Std_Dev` FLOAT NOT NULL,
  `fyk` FLOAT NOT NULL,
  `fsu_m` FLOAT NULL,
  `fsu_Std_Dev` FLOAT NULL,
  `Est_Ductility_Class` ENUM('A', 'B', 'C') NULL,
  `Elastic_Modulus` FLOAT NULL,
  `Ult_Strain` FLOAT NULL,
  `Fracture_Strain` FLOAT NULL,
  `Profile` VARCHAR(45) NULL,
  `Notes` TEXT NULL,
  PRIMARY KEY (`Test_Region_ID`, `Element_ID`),
  INDEX `fk_Reinforcement_Testing_Test_Region1_idx` (`Element_ID` ASC, `Test_Region_ID` ASC) VISIBLE,
  CONSTRAINT `fk_Reinforcement_Testing_Test_Region1`
    FOREIGN KEY (`Element_ID` , `Test_Region_ID`)
    REFERENCES `element_database_core`.`Test_Region` (`Element_ID` , `Test_Region_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `element_database_core`.`HCS_Damage_Catalogue`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `element_database_core`.`HCS_Damage_Catalogue` (
  `Element_ID` CHAR(36) NOT NULL,
  `Product_ID` VARCHAR(30) NULL,
  `T1_Cracks` JSON NULL,
  `T2_Cracks` JSON NULL,
  `T3_Cracks` JSON NULL,
  `T4_Cracks` JSON NULL,
  `T5_Cracks` JSON NULL,
  `T6_Cracks` JSON NULL,
  `T7_Cracks` JSON NULL,
  `T8_Cracks` JSON NULL,
  `T9_Cracks` JSON NULL,
  `T10_Cracks` JSON NULL,
  `Reuse_Class` ENUM('Full capacity', 'Downcycle') NULL,
  `Photo_Path` VARCHAR(1000) NULL,
  `Notes` TEXT NULL,
  INDEX `fk_HCS_Damage_Catalogue_HCS_Geometry1_idx` (`Product_ID` ASC) VISIBLE,
  PRIMARY KEY (`Element_ID`),
  CONSTRAINT `fk_HCS_Damage_Catalogue_HCS_Geometry1`
    FOREIGN KEY (`Product_ID`)
    REFERENCES `element_database_core`.`HCS_Geometry` (`Product_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_HCS_Damage_Catalogue_Slab_Element1`
    FOREIGN KEY (`Element_ID`)
    REFERENCES `element_database_core`.`Slab_Element` (`Element_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `element_database_core`.`Full_Scale_Testing`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `element_database_core`.`Full_Scale_Testing` (
  `Test_Region_ID` INT UNSIGNED NOT NULL,
  `Element_ID` CHAR(36) NOT NULL,
  `Bending` FLOAT NULL,
  `Shear` FLOAT NULL,
  `Anchorage_Capacity` FLOAT NULL,
  `Axial_Comp` FLOAT NULL,
  `Flexure_Shear` FLOAT NULL,
  `Buckling` FLOAT NULL,
  `Torsion` FLOAT NULL,
  `Support_Conditions` VARCHAR(100) NULL,
  PRIMARY KEY (`Test_Region_ID`, `Element_ID`),
  CONSTRAINT `fk_Full_Scale_Testing_Test_Region1`
    FOREIGN KEY (`Test_Region_ID` , `Element_ID`)
    REFERENCES `element_database_core`.`Test_Region` (`Test_Region_ID` , `Element_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `element_database_core`.`LCA_EPD`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `element_database_core`.`LCA_EPD` (
  `Element_ID` CHAR(36) NOT NULL,
  `A1` JSON NULL,
  `A2` JSON NULL,
  `A3` JSON NULL,
  `A4` JSON NULL,
  PRIMARY KEY (`Element_ID`),
  CONSTRAINT `fk_LCA_EPD_Element_Super1`
    FOREIGN KEY (`Element_ID`)
    REFERENCES `element_database_core`.`Element_Super` (`Element_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `element_database_core`.`LCC`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `element_database_core`.`LCC` (
  `Element_ID` CHAR(36) NOT NULL,
  `Building_ID` VARCHAR(45) NOT NULL,
  `Deconstruction_Cost` FLOAT NOT NULL,
  `Num_Reclaimed_Elmts` INT NOT NULL,
  `Transport_Exp_tkm` FLOAT NOT NULL,
  `Est_Cost_Per_Elmt` FLOAT NOT NULL,
  INDEX `fk_LCC_Circularity_Data1_idx` (`Building_ID` ASC) VISIBLE,
  INDEX `fk_LCC_LCA_EPD1_idx` (`Element_ID` ASC) VISIBLE,
  PRIMARY KEY (`Element_ID`),
  CONSTRAINT `fk_LCC_Circularity_Data1`
    FOREIGN KEY (`Building_ID`)
    REFERENCES `element_database_core`.`Circularity_Data` (`Building_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_LCC_LCA_EPD1`
    FOREIGN KEY (`Element_ID`)
    REFERENCES `element_database_core`.`LCA_EPD` (`Element_ID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

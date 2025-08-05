SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema element_database_analysis
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema element_database_analysis
-- -----------------------------------------------------
-- Drop existing database if it exists
DROP DATABASE IF EXISTS `element_database_anal`;

CREATE SCHEMA IF NOT EXISTS `element_database_anal` DEFAULT CHARACTER SET utf8 ;
USE `element_database_anal` ;

-- -----------------------------------------------------
-- Table `element_database_anal`.`Wall_Capacity`
-- -----------------------------------------------------
CREATE TABLE `Wall_Capacity` (
  `Product_ID` VARCHAR(30) NOT NULL,
  `Reinf_ID` VARCHAR(30) NOT NULL,
  `bending_pos_kN` DECIMAL(10,3) NULL,
  `bending_neg_kN` DECIMAL(10,3) NULL,
  `p_delta_kN` DECIMAL(10,3) NULL,
  `axial_comp_kN` DECIMAL(10,3) NULL,
  `axial_tens_kN` DECIMAL(10,3) NULL,
  `shear_dt_kN` DECIMAL(10,3) NULL,
  `shear_base_kN` DECIMAL(10,3) NULL,
  `support_conds` VARCHAR(100) NULL,
  `limit_state` VARCHAR(15) NULL,
  `reference_code` VARCHAR(100),
  PRIMARY KEY (`Product_ID`),
  -- Foreign key back to phys.Wall_Geometry
  CONSTRAINT `fk_anal_wall_geom_phys`
    FOREIGN KEY (`Product_ID`)
    REFERENCES `element_database_phys`.`Wall_Geometry` (`Product_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  -- Foreign key back to phys.Wall_Long_Reinf
  CONSTRAINT `fk_anal_wall_reinf_phys`
    FOREIGN KEY (`Reinf_ID`)
    REFERENCES `element_database_phys`.`Wall_Long_Reinf` (`Reinf_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Table `element_database_anal`.`Beam_Capacity`
-- -----------------------------------------------------
CREATE TABLE `Beam_Capacity` (
  `Product_ID` VARCHAR(30) NOT NULL,
  `Reinf_ID` VARCHAR(30) NOT NULL,
  `bending_pos_kN` DECIMAL(10,3) NULL,
  `bending_neg_kN` DECIMAL(10,3) NULL,
  `shear_dt_kN` DECIMAL(10,3) NULL,
  `shear_web_kN` DECIMAL(10,3) NULL,
  `flex_shear_int_kN` DECIMAL(10,3) NULL,
  `torsion_kN` DECIMAL(10,3) NULL,
  `bond_slip_kN` DECIMAL(10,3) NULL,
  `bearing_kN` DECIMAL(10,3) NULL,
  `support_conds` VARCHAR(100) NULL,
  `limit_state` VARCHAR(15) NULL,
  `reference_code` VARCHAR(100),
  PRIMARY KEY (`Product_ID`),
  -- Foreign key back to phys.Beam_Geometry
  CONSTRAINT `fk_anal_beam_geom_phys`
    FOREIGN KEY (`Product_ID`)
    REFERENCES `element_database_phys`.`Beam_Geometry` (`Product_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  -- Foreign key back to phys.Beam_Long_Reinf
  CONSTRAINT `fk_anal_beam_reinf_phys`
    FOREIGN KEY (`Reinf_ID`)
    REFERENCES `element_database_phys`.`Beam_Long_Reinf` (`Reinf_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Table `element_database_anal`.`Column_Capacity`
-- -----------------------------------------------------
CREATE TABLE `Column_Capacity` (
  `Product_ID` VARCHAR(30) NOT NULL,
  `Reinf_ID` VARCHAR(30) NOT NULL,
  `axial_comp_kN` DECIMAL(10,3) NULL,
  `axial_tens_kN` DECIMAL(10,3) NULL,
  `uni_single_bending_kN` DECIMAL(10,3) NULL,
  `uni_double_bending_kN` DECIMAL(10,3) NULL,
  `biax_single_bending_kN` DECIMAL(10,3) NULL,
  `biax_double_bending_kN` DECIMAL(10,3) NULL,
  `buckling_kN` DECIMAL(10,3) NULL,
  `shear_kN` DECIMAL(10,3) NULL,
  `torsion_kN` DECIMAL(10,3) NULL,
  `confinement_kN` DECIMAL(10,3) NULL,
  `support_conds` VARCHAR(100) NULL,
  `limit_state` VARCHAR(15) NULL,
  `reference_code` VARCHAR(100),
  PRIMARY KEY (`Product_ID`),
  -- Foreign key back to phys.Column_Geometry
  CONSTRAINT `fk_anal_column_geom_phys`
    FOREIGN KEY (`Product_ID`)
    REFERENCES `element_database_phys`.`Column_Geometry` (`Product_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  -- Foreign key back to phys.Column_Long_Reinf
  CONSTRAINT `fk_anal_column_reinf_phys`
    FOREIGN KEY (`Reinf_ID`)
    REFERENCES `element_database_phys`.`Column_Long_Reinf` (`Reinf_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Table `element_database_anal`.`Corbel_Capacity`
-- -----------------------------------------------------
CREATE TABLE `Corbel_Capacity` (
  `Corbel_ID` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `Wall_Product_ID` VARCHAR(30) NULL,
  `Beam_Product_ID` VARCHAR(30) NULL,
  `Column_Product_ID` VARCHAR(30) NULL,
  `Wall_Zone_ID` VARCHAR(30) NULL,
  `Beam_Zone_ID` VARCHAR(30) NULL,
  `Column_Zone_ID` VARCHAR(30) NULL,
  `axial_comp_kN` DECIMAL(10,3) NULL,
  `axial_tens_kN` DECIMAL(10,3) NULL,
  `tension_tie_kN` DECIMAL(10,3) NULL,
  `anchorage_kN` DECIMAL(10,3) NULL,
  `shear_dt_kN` DECIMAL(10,3) NULL,
  `shear_friction_kN` DECIMAL(10,3) NULL,
  `bearing_kN` DECIMAL(10,3) NULL,
  `torsion_kN` DECIMAL(10,3) NULL,
  `limit_state` VARCHAR(15) NULL,
  `reference_code` VARCHAR(100),
  PRIMARY KEY (`Corbel_ID`),
  -- link back to the Corbel_Geometry table that owns this corbel
  CONSTRAINT `fk_phys_corbel_to_phys_corbel`
    FOREIGN KEY (`Corbel_ID`)
    REFERENCES `element_database_phys`.`Corbel_Geometry` (`Corbel_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  -- informational link back to the parent element geometry
  CONSTRAINT `fk_phys_corbel_to_wall_phys`
    FOREIGN KEY (`Wall_Product_ID`)
    REFERENCES `element_database_phys`.`Corbel_Geometry` (`Wall_Product_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_phys_corbel_to_beam_phys`
    FOREIGN KEY (`Beam_Product_ID`)
    REFERENCES `element_database_phys`.`Corbel_Geometry` (`Beam_Product_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
CONSTRAINT `fk_phys_corbel_to_column_phys`
    FOREIGN KEY (`Column_Product_ID`)
    REFERENCES `element_database_phys`.`Corbel_Geometry` (`Column_Product_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  -- informational link back to the zone reinforcement ("*_C")
  CONSTRAINT `fk_phys_corbel_to_wall_zone_phys`
    FOREIGN KEY (`Wall_Zone_ID`)
    REFERENCES `element_database_phys`.`Wall_Zone_Geometry` (`Zone_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_phys_corbel_to_beam_zone_phys`
    FOREIGN KEY (`Beam_Zone_ID`)
    REFERENCES `element_database_phys`.`Beam_Zone_Geometry` (`Zone_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
CONSTRAINT `fk_phys_corbel_to_column_zone_phys`
    FOREIGN KEY (`Column_Zone_ID`)
    REFERENCES `element_database_phys`.`Column_Zone_Geometry` (`Zone_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Table `element_database_anal`.`1W_Slab_Capacity`
-- -----------------------------------------------------
CREATE TABLE `1W_Slab_Capacity` (
  `Product_ID` VARCHAR(30) NOT NULL,
  `Reinf_ID` VARCHAR(30) NOT NULL,
  `bending_pos_kN` DECIMAL(10,3) NULL,
  `bending_neg_kN` DECIMAL(10,3) NULL,
  `shear_kN` DECIMAL(10,3) NULL,
  `punching_shear_kN` DECIMAL(10,3) NULL,
  `torsion_kN` DECIMAL(10,3) NULL,
  `support_conds` VARCHAR(100) NULL,
  `limit_state` VARCHAR(15) NULL,
  `reference_code` VARCHAR(100),
  PRIMARY KEY (`Product_ID`),
  -- Foreign key back to phys.Slab_Geometry
  CONSTRAINT `fk_anal_slab1w_geom_phys`
    FOREIGN KEY (`Product_ID`)
    REFERENCES `element_database_phys`.`Slab_Geometry` (`Product_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  -- Foreign key back to phys.Slab_Long_Reinf
  CONSTRAINT `fk_anal_slab1w_reinf_phys`
    FOREIGN KEY (`Reinf_ID`)
    REFERENCES `element_database_phys`.`Slab_Long_Reinf` (`Reinf_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Table `element_database_anal`.`2W_Slab_Capacity`
-- -----------------------------------------------------
CREATE TABLE `2W_Slab_Capacity` (
  `Product_ID` VARCHAR(30) NOT NULL,
  `Reinf_ID` VARCHAR(30) NOT NULL,
  `bending_pos_kN` DECIMAL(10,3) NULL,
  `bending_neg_kN` DECIMAL(10,3) NULL,
  `shear_kN` DECIMAL(10,3) NULL,
  `punching_shear_kN` DECIMAL(10,3) NULL,
  `torsion_kN` DECIMAL(10,3) NULL,
  `support_conds` VARCHAR(100) NULL,
  `limit_state` VARCHAR(15) NULL,
  `reference_code` VARCHAR(100),
  PRIMARY KEY (`Product_ID`),
  -- Foreign key back to phys.Slab_Geometry
  CONSTRAINT `fk_anal_slab2w_geom_phys`
    FOREIGN KEY (`Product_ID`)
    REFERENCES `element_database_phys`.`Slab_Geometry` (`Product_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  -- Foreign key back to phys.Slab_Long_Reinf
  CONSTRAINT `fk_anal_slab2w_reinf_phys`
    FOREIGN KEY (`Reinf_ID`)
    REFERENCES `element_database_phys`.`Slab_Long_Reinf` (`Reinf_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Table `element_database_anal`.`HCS_Capacity`
-- -----------------------------------------------------
CREATE TABLE `HCS_Capacity` (
  `Product_ID` VARCHAR(30) NOT NULL,
  `Reinf_ID` VARCHAR(30) NOT NULL,
  `bending_pos_kN` DECIMAL(10,3) NULL,
  `bending_neg_kN` DECIMAL(10,3) NULL,
  `anchorage_kN` DECIMAL(10,3) NULL,
  `punching_shear_kN` DECIMAL(10,3) NULL,
  `flex_shear_int_kN` DECIMAL(10,3) NULL,
  `long_splitting_kN` DECIMAL(10,3) NULL,
  `support_conds` VARCHAR(100) NULL,
  `limit_state` VARCHAR(15) NULL,
  `reference_code` VARCHAR(100),
  PRIMARY KEY (`Product_ID`),
  -- Foreign key back to core.HCS_Geometry
  CONSTRAINT `fk_anal_slab_geom_core`
    FOREIGN KEY (`Product_ID`)
    REFERENCES `element_database_core`.`HCS_Geometry` (`Product_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  -- Foreign key back to phys.Slab_Long_Reinf
  CONSTRAINT `fk_anal_slab_prestr_phys`
    FOREIGN KEY (`Reinf_ID`)
    REFERENCES `element_database_phys`.`HCS_Prestressing` (`Reinf_ID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB;




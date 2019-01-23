-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema wall
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema wall
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `wall` DEFAULT CHARACTER SET utf8 ;
USE `wall` ;

-- -----------------------------------------------------
-- Table `wall`.`users`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `wall`.`users` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `f_n` VARCHAR(255) NOT NULL,
  `l_n` VARCHAR(255) NOT NULL,
  `email` VARCHAR(255) NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  `created_at` DATETIME NOT NULL,
  `updated_at` DATETIME NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `wall`.`messages`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `wall`.`messages` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `message` TEXT NOT NULL,
  `created_at` DATETIME NOT NULL,
  `updated_at` DATETIME NOT NULL,
  `user_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_messages_users_idx` (`user_id` ASC) VISIBLE,
  CONSTRAINT `fk_messages_users`
    FOREIGN KEY (`user_id`)
    REFERENCES `wall`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `wall`.`comments`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `wall`.`comments` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `comment` TEXT NOT NULL,
  `created_at` DATETIME NOT NULL,
  `updated_at` DATETIME NOT NULL,
  `user_id` INT NOT NULL,
  `message_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_comments_users1_idx` (`user_id` ASC) VISIBLE,
  INDEX `fk_comments_messages1_idx` (`message_id` ASC) VISIBLE,
  CONSTRAINT `fk_comments_users1`
    FOREIGN KEY (`user_id`)
    REFERENCES `wall`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_comments_messages1`
    FOREIGN KEY (`message_id`)
    REFERENCES `wall`.`messages` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

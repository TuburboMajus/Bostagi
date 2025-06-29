/******************************\
 *  INITIALIZE
\******************************/ 

drop database IF EXISTS $database;
create database $database;
use $database;


/******************************\
 * TABLES
\******************************/ 



/***** APP *****/

create table bostagi(
    version varchar(20) primary key not null
);

create table language(
	code varchar(2) primary key not null,
	name varchar(50) not null
);


/***** USER *****/
create table privilege(
    id varchar(36) primary key not null,
    label varchar(256) not null unique,
    roles varchar(256) not null,
    editable bool not null default 1
);


create table user(
    id varchar(36) primary key not null,
    privilege varchar(36) not null,
    username varchar(320) not null,
    password binary(60) not null,
    is_authenticated bool not null default 0,
    is_active bool not null default 0,
    is_disabled bool not null default 0,
    language varchar(256) not null default "en",
    foreign key (language) references language(code),
    foreign key (privilege) references privilege(id)
);
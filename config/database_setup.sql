--------- user setting tables ---------

create table dbo.departments (
	department_key varchar(255) not null constraint unique_department_key default newid(),
	department nvarchar(50) not null,
	constraint pk_departments primary key (department_key)
);

INSERT INTO btn.dbo.departments
(department)
VALUES(N'Phòng Công Nghệ Thông Tin');
INSERT INTO btn.dbo.departments
(department)
VALUES(N'Tư lệnh Và Cấp Chỉ Huy');
INSERT INTO btn.dbo.departments
(department)
VALUES(N'Công Ty Cổ Phần Giải Pháp CNTT Tân Cảng');
INSERT INTO btn.dbo.departments
(department)
VALUES(N'Phòng Tài Chính - Kế Toán');

create table dbo.roles (
	role_key varchar(255) not null constraint unique_role_key default newid(),
	role_name nvarchar(10) not null,
	constraint pk_roles primary key (role_key)
);

INSERT INTO btn.dbo.roles
(role_name)
VALUES(N'ADMIN');
INSERT INTO btn.dbo.roles
(role_name)
VALUES(N'VIEWER');
INSERT INTO btn.dbo.roles
(role_name)
VALUES(N'EDITOR');

create table dbo.users (
	user_key varchar(255) not null constraint unique_user_key default newid(),
	user_name varchar(255) not null,
	pass_word varchar(255) not null,
	email varchar(255) null,
	phone_number varchar(100) null,
	role_key varchar(255) null,
	first_name nvarchar(50) null,
	middle_name nvarchar(50) null,
	last_name nvarchar(50) null,
	department_key varchar(255) null,
	constraint unique_user_name unique (user_name),
	constraint pk_users primary key (user_key)
);

create unique nonclustered index uq_users_email on dbo.users (email asc);

alter table dbo.users add constraint fk_users_departments foreign key (department_key) references dbo.departments(department_key);
alter table dbo.users add constraint fk_users_roles foreign key (role_key) references dbo.roles(role_key);

--------- business tables ---------

-- dbo.receipts:
create table dbo.recepits (
	receipt_key varchar(255) not null constraint unique_receipt_key default newid(),
	receipt_code char(10) not null,
	receipt_date datetime2 not null,
	shipment_code varchar(10) not null,
	invoice_number varchar(10) not null,
	customer_key varchar(255) not null,
	constraint pk_receipts primary key (receipt_key),
	constraint fk_receipts_customers foreign key (customer_key) references dbo.customers (customer_key)
);

-- dbo.customers:
create table dbo.customers (
	customer_key varchar(255) not null constraint unique_customer_key default newid(),
	tax_code varchar(11) not null,
	customer_name nvarchar(255) not null,
	address nvarchar(255) null,
	province_key varchar(255) not null,
	start_time datetime2 default getdate() not null,
	end_time datetime2 null,
	is_active char(1) default 'y' not null,
	constraint pk_customers primary key (customer_key),
	constraint fk_customers_provinces foreign key (province_key) references dbo.provinces(province_key)
);

-- dbo.provinces:
create table dbo.provinces (
	province_key varchar(255) not null constraint unique_province_key default newid(),
	old_province nvarchar(100) not null,
	new_province nvarchar(100) not null,
	zone nvarchar(100) null,
	start_time datetime2 default getdate() not null,
	end_time datetime2 null,
	is_active char(1) default 'y' not null,
	constraint pk_provinces primary key (province_key)
);

INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Hà Tĩnh', N'Hà Tĩnh', N'Bắc Trung Bộ');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Hà Nam', N'Ninh Bình', N'Bắc Trung Bộ');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Quảng Trị', N'Quảng Trị', N'Bắc Trung Bộ');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Tuyên Quang', N'Tuyên Quang', N'Đông Bắc Bộ');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Tây Ninh', N'Tây Ninh', N'Đông Nam Bộ Và Đồng Bằng Sông Cửu Long');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Yên Bái', N'Lào Cai', N'Tây Bắc Bộ');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Phú Yên', N'Đắk Lắk', N'Duyên Hải Nam Trung Bộ Và Tây Nguyên');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Lạng Sơn', N'Lạng Sơn', N'Đông Bắc Bộ');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Khánh Hoà', N'Khánh Hoà', N'Duyên Hải Nam Trung Bộ Và Tây Nguyên');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Cà Mau', N'Cà Mau', N'Đông Nam Bộ Và Đồng Bằng Sông Cửu Long');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Lào Cai', N'Lào Cai', N'Tây Bắc Bộ');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Lai Châu', N'Lai Châu', N'Tây Bắc Bộ');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Sóc Trăng', N'Cần Thơ', N'Đông Nam Bộ Và Đồng Bằng Sông Cửu Long');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Sơn La', N'Sơn La', N'Tây Bắc Bộ');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Nam Định', N'Ninh Bình', N'Bắc Trung Bộ');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Vĩnh Phúc', N'Phú Thọ', N'Đồng Bằng Sông Hồng');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Kiên Giang', N'An Giang', N'Đông Nam Bộ Và Đồng Bằng Sông Cửu Long');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Long An', N'Tây Ninh', N'Đông Nam Bộ Và Đồng Bằng Sông Cửu Long');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Gia Lai', N'Gia Lai', N'Duyên Hải Nam Trung Bộ Và Tây Nguyên');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Thừa Thiên Huế', N'Huế', N'Duyên Hải Nam Trung Bộ Và Tây Nguyên');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Hải Phòng', N'Hải Phòng', N'Đồng Bằng Sông Hồng');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Tiền Giang', N'Đồng Tháp', N'Đông Nam Bộ Và Đồng Bằng Sông Cửu Long');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Quảng Nam', N'Đà Nẵng', N'Duyên Hải Nam Trung Bộ Và Tây Nguyên');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'An Giang', N'An Giang', N'Đông Nam Bộ Và Đồng Bằng Sông Cửu Long');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Điện Biên', N'Điện Biên', N'Tây Bắc Bộ');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Hà Nội', N'Hà Nội', N'Đồng Bằng Sông Hồng');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Bình Dương', N'Hồ Chí Minh', N'Đông Nam Bộ Và Đồng Bằng Sông Cửu Long');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Đồng Tháp', N'Đồng Tháp', N'Đông Nam Bộ Và Đồng Bằng Sông Cửu Long');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Bạc Liêu', N'Cà Mau', N'Đông Nam Bộ Và Đồng Bằng Sông Cửu Long');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Quảng Bình', N'Quảng Trị', N'Bắc Trung Bộ');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Cao Bằng', N'Cao Bằng', N'Đông Bắc Bộ');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Vĩnh Long', N'Vĩnh Long', N'Đông Nam Bộ Và Đồng Bằng Sông Cửu Long');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Đắk Nông', N'Lâm Đồng', N'Duyên Hải Nam Trung Bộ Và Tây Nguyên');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Ninh Thuận', N'Khánh Hoà', N'Duyên Hải Nam Trung Bộ Và Tây Nguyên');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Hưng Yên', N'Hưng Yên', N'Đồng Bằng Sông Hồng');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Đồng Nai', N'Đồng Nai', N'Đông Nam Bộ Và Đồng Bằng Sông Cửu Long');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Hậu Giang', N'Cần Thơ', N'Đông Nam Bộ Và Đồng Bằng Sông Cửu Long');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Thanh Hoá', N'Thanh Hoá', N'Bắc Trung Bộ');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Quảng Ninh', N'Quảng Ninh', N'Đông Bắc Bộ');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Bắc Ninh', N'Bắc Ninh', N'Đồng Bằng Sông Hồng');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Thái Bình', N'Hưng Yên', N'Đồng Bằng Sông Hồng');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Nghệ An', N'Nghệ An', N'Bắc Trung Bộ');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Đà Nẵng', N'Đà Nẵng', N'Duyên Hải Nam Trung Bộ Và Tây Nguyên');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Quảng Ngãi', N'Quảng Ngãi', N'Duyên Hải Nam Trung Bộ Và Tây Nguyên');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Bà Rịa - Vũng Tàu', N'Hồ Chí Minh', N'Đông Nam Bộ Và Đồng Bằng Sông Cửu Long');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Lâm Đồng', N'Lâm Đồng', N'Duyên Hải Nam Trung Bộ Và Tây Nguyên');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Bình Định', N'Gia Lai', N'Duyên Hải Nam Trung Bộ Và Tây Nguyên');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Trà Vinh', N'Vĩnh Long', N'Đông Nam Bộ Và Đồng Bằng Sông Cửu Long');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Hoà Bình', N'Phú Thọ', N'Đồng Bằng Sông Hồng');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Hải Dương', N'Hải Phòng', N'Đồng Bằng Sông Hồng');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Cần Thơ', N'Cần Thơ', N'Đông Nam Bộ Và Đồng Bằng Sông Cửu Long');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Đắk Lắk', N'Đắk Lắk', N'Duyên Hải Nam Trung Bộ Và Tây Nguyên');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Hà Giang', N'Tuyên Quang', N'Đông Bắc Bộ');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Phú Thọ', N'Phú Thọ', N'Đồng Bằng Sông Hồng');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Bắc Giang', N'Bắc Ninh', N'Đồng Bằng Sông Hồng');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Kon Tum', N'Quảng Ngãi', N'Duyên Hải Nam Trung Bộ Và Tây Nguyên');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Bến Tre', N'Vĩnh Long', N'Đông Nam Bộ Và Đồng Bằng Sông Cửu Long');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Ninh Bình', N'Ninh Bình', N'Bắc Trung Bộ');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Bình Thuận', N'Lâm Đồng', N'Duyên Hải Nam Trung Bộ Và Tây Nguyên');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Bắc Kạn', N'Thái Nguyên', N'Đông Bắc Bộ');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Hồ Chí Minh', N'Hồ Chí Minh', N'Đông Nam Bộ Và Đồng Bằng Sông Cửu Long');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Bình Phước', N'Đồng Nai', N'Đông Nam Bộ Và Đồng Bằng Sông Cửu Long');
INSERT INTO btn.dbo.provinces
(old_province, new_province, [zone])
VALUES(N'Thái Nguyên', N'Thái Nguyên', N'Đông Bắc Bộ');

-- dbo.containers:
create table dbo.containers (
	container_key varchar(255) not null constraint unique_container_key default newid(),
	container_size int not null,
	container_status char(1) null,
	container_type char(2) null,
	start_time datetime2 default getdate() not null,
	end_time datetime2 null,
	is_active char(1) default 'y' not null,
	constraint pk_containers primary key (container_key)
);

-- dbo.services:
create table dbo.services (
	service_key varchar(255) not null constraint unique_service_key default newid(),
	service_name nvarchar(100) not null,
	container_key varchar(255) not null,
	from_date datetime2 null,
	to_date datetime2 null,
	unit_price int default 0 null,
	tax_rate int default 0 null,
	start_time datetime2 default getdate() not null,
	end_time datetime2 null,
	is_active char(1) default 'y' not null,
	constraint pk_services primary key (service_key),
	constraint fk_services_containers foreign key (container_key) references dbo.containers(container_key)
);

-- dbo.lines:
create table dbo.lines (
	line_key varchar(255) not null constraint unique_line_key default newid(),
	receipt_key varchar(255) not null,
	container_number varchar(11) not null,
	service_key varchar(255) not null,
	quantity int,
	discount int,
	amount int,
	constraint pk_lines primary key (line_key),
	constraint fk_lines_receipts foreign key (receipt_key) references dbo.receipts (receipt_key),
	constraint fk_lines_services foreign key (service_key) references dbo.services (service_key)
);

--------- test tables ---------

--------- user setting tables ---------

create table dbo.test_departments (
	department_key varchar(255) not null constraint unique_test_department_key default newid(),
	department nvarchar(50) not null,
	constraint pk_test_departments primary key (department_key)
);

INSERT INTO btn.dbo.test_departments
(department)
VALUES(N'Phòng Công Nghệ Thông Tin');
INSERT INTO btn.dbo.test_departments
(department)
VALUES(N'Tư lệnh Và Cấp Chỉ Huy');
INSERT INTO btn.dbo.test_departments
(department)
VALUES(N'Công Ty Cổ Phần Giải Pháp CNTT Tân Cảng');
INSERT INTO btn.dbo.test_departments
(department)
VALUES(N'Phòng Tài Chính - Kế Toán');

create table dbo.test_roles (
	role_key varchar(255) not null constraint unique_test_role_key default newid(),
	role_name nvarchar(10) not null,
	constraint pk_test_roles primary key (role_key)
);

create table dbo.test_users (
	user_key varchar(255) not null constraint unique_test_user_key default newid(),
	user_name varchar(255) not null,
	pass_word varchar(255) not null,
	email varchar(255) null,
	phone_number varchar(100) null,
	role_key varchar(255) null,
	first_name nvarchar(50) null,
	middle_name nvarchar(50) null,
	last_name nvarchar(50) null,
	department_key varchar(255) null,
	constraint unique_test_user_name unique (user_name),
	constraint pk_test_users primary key (user_key)
);

create unique nonclustered index uq_test_users_email on dbo.test_users (email asc);

alter table dbo.test_users add constraint fk_test_users_departments foreign key (department_key) references dbo.test_departments(department_key);
alter table dbo.test_users add constraint fk_test_users_roles foreign key (role_key) references dbo.test_roles(role_key);

--------- business tables ---------

-- dbo.test_receipts:
create table dbo.test_receipts (
	receipt_key varchar(255) not null constraint unique_test_receipt_key default newid(),
	receipt_code char(10) not null,
	receipt_date datetime2 not null,
	shipment_code varchar(10) not null,
	invoice_number varchar(10) not null,
	customer_key varchar(255) not null,
	constraint pk_test_receipts primary key (receipt_key),
	constraint fk_test_receipts_customers foreign key (customer_key) references dbo.test_customers (customer_key)
);

-- dbo.test_customers:
create table dbo.test_customers (
	customer_key varchar(255) not null constraint unique_test_customer_key default newid(),
	tax_code varchar(11) not null,
	customer_name nvarchar(255) not null,
	address nvarchar(255) null,
	province_key varchar(255) not null,
	start_time datetime2 default getdate() not null,
	end_time datetime2 null,
	is_active char(1) default 'y' not null,
	constraint pk_test_customers primary key (customer_key),
	constraint fk_test_customers_provinces foreign key (province_key) references dbo.test_provinces(province_key)
);

-- dbo.test_provinces:
create table dbo.test_provinces (
	province_key varchar(255) not null constraint unique_test_province_key default newid(),
	old_province nvarchar(100) not null,
	new_province nvarchar(100) not null,
	zone nvarchar(100) null,
	start_time datetime2 default getdate() not null,
	end_time datetime2 null,
	is_active char(1) default 'y' not null,
	constraint pk_test_provinces primary key (province_key)
);

INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Hà Tĩnh', N'Hà Tĩnh', N'Bắc Trung Bộ');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Hà Nam', N'Ninh Bình', N'Bắc Trung Bộ');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Quảng Trị', N'Quảng Trị', N'Bắc Trung Bộ');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Tuyên Quang', N'Tuyên Quang', N'Đông Bắc Bộ');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Tây Ninh', N'Tây Ninh', N'Đông Nam Bộ Và Đồng Bằng Sông Cửu Long');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Yên Bái', N'Lào Cai', N'Tây Bắc Bộ');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Phú Yên', N'Đắk Lắk', N'Duyên Hải Nam Trung Bộ Và Tây Nguyên');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Lạng Sơn', N'Lạng Sơn', N'Đông Bắc Bộ');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Khánh Hoà', N'Khánh Hoà', N'Duyên Hải Nam Trung Bộ Và Tây Nguyên');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Cà Mau', N'Cà Mau', N'Đông Nam Bộ Và Đồng Bằng Sông Cửu Long');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Lào Cai', N'Lào Cai', N'Tây Bắc Bộ');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Lai Châu', N'Lai Châu', N'Tây Bắc Bộ');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Sóc Trăng', N'Cần Thơ', N'Đông Nam Bộ Và Đồng Bằng Sông Cửu Long');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Sơn La', N'Sơn La', N'Tây Bắc Bộ');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Nam Định', N'Ninh Bình', N'Bắc Trung Bộ');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Vĩnh Phúc', N'Phú Thọ', N'Đồng Bằng Sông Hồng');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Kiên Giang', N'An Giang', N'Đông Nam Bộ Và Đồng Bằng Sông Cửu Long');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Long An', N'Tây Ninh', N'Đông Nam Bộ Và Đồng Bằng Sông Cửu Long');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Gia Lai', N'Gia Lai', N'Duyên Hải Nam Trung Bộ Và Tây Nguyên');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Thừa Thiên Huế', N'Huế', N'Duyên Hải Nam Trung Bộ Và Tây Nguyên');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Hải Phòng', N'Hải Phòng', N'Đồng Bằng Sông Hồng');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Tiền Giang', N'Đồng Tháp', N'Đông Nam Bộ Và Đồng Bằng Sông Cửu Long');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Quảng Nam', N'Đà Nẵng', N'Duyên Hải Nam Trung Bộ Và Tây Nguyên');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'An Giang', N'An Giang', N'Đông Nam Bộ Và Đồng Bằng Sông Cửu Long');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Điện Biên', N'Điện Biên', N'Tây Bắc Bộ');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Hà Nội', N'Hà Nội', N'Đồng Bằng Sông Hồng');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Bình Dương', N'Hồ Chí Minh', N'Đông Nam Bộ Và Đồng Bằng Sông Cửu Long');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Đồng Tháp', N'Đồng Tháp', N'Đông Nam Bộ Và Đồng Bằng Sông Cửu Long');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Bạc Liêu', N'Cà Mau', N'Đông Nam Bộ Và Đồng Bằng Sông Cửu Long');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Quảng Bình', N'Quảng Trị', N'Bắc Trung Bộ');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Cao Bằng', N'Cao Bằng', N'Đông Bắc Bộ');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Vĩnh Long', N'Vĩnh Long', N'Đông Nam Bộ Và Đồng Bằng Sông Cửu Long');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Đắk Nông', N'Lâm Đồng', N'Duyên Hải Nam Trung Bộ Và Tây Nguyên');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Ninh Thuận', N'Khánh Hoà', N'Duyên Hải Nam Trung Bộ Và Tây Nguyên');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Hưng Yên', N'Hưng Yên', N'Đồng Bằng Sông Hồng');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Đồng Nai', N'Đồng Nai', N'Đông Nam Bộ Và Đồng Bằng Sông Cửu Long');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Hậu Giang', N'Cần Thơ', N'Đông Nam Bộ Và Đồng Bằng Sông Cửu Long');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Thanh Hoá', N'Thanh Hoá', N'Bắc Trung Bộ');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Quảng Ninh', N'Quảng Ninh', N'Đông Bắc Bộ');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Bắc Ninh', N'Bắc Ninh', N'Đồng Bằng Sông Hồng');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Thái Bình', N'Hưng Yên', N'Đồng Bằng Sông Hồng');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Nghệ An', N'Nghệ An', N'Bắc Trung Bộ');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Đà Nẵng', N'Đà Nẵng', N'Duyên Hải Nam Trung Bộ Và Tây Nguyên');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Quảng Ngãi', N'Quảng Ngãi', N'Duyên Hải Nam Trung Bộ Và Tây Nguyên');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Bà Rịa - Vũng Tàu', N'Hồ Chí Minh', N'Đông Nam Bộ Và Đồng Bằng Sông Cửu Long');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Lâm Đồng', N'Lâm Đồng', N'Duyên Hải Nam Trung Bộ Và Tây Nguyên');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Bình Định', N'Gia Lai', N'Duyên Hải Nam Trung Bộ Và Tây Nguyên');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Trà Vinh', N'Vĩnh Long', N'Đông Nam Bộ Và Đồng Bằng Sông Cửu Long');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Hoà Bình', N'Phú Thọ', N'Đồng Bằng Sông Hồng');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Hải Dương', N'Hải Phòng', N'Đồng Bằng Sông Hồng');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Cần Thơ', N'Cần Thơ', N'Đông Nam Bộ Và Đồng Bằng Sông Cửu Long');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Đắk Lắk', N'Đắk Lắk', N'Duyên Hải Nam Trung Bộ Và Tây Nguyên');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Hà Giang', N'Tuyên Quang', N'Đông Bắc Bộ');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Phú Thọ', N'Phú Thọ', N'Đồng Bằng Sông Hồng');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Bắc Giang', N'Bắc Ninh', N'Đồng Bằng Sông Hồng');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Kon Tum', N'Quảng Ngãi', N'Duyên Hải Nam Trung Bộ Và Tây Nguyên');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Bến Tre', N'Vĩnh Long', N'Đông Nam Bộ Và Đồng Bằng Sông Cửu Long');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Ninh Bình', N'Ninh Bình', N'Bắc Trung Bộ');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Bình Thuận', N'Lâm Đồng', N'Duyên Hải Nam Trung Bộ Và Tây Nguyên');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Bắc Kạn', N'Thái Nguyên', N'Đông Bắc Bộ');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Hồ Chí Minh', N'Hồ Chí Minh', N'Đông Nam Bộ Và Đồng Bằng Sông Cửu Long');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Bình Phước', N'Đồng Nai', N'Đông Nam Bộ Và Đồng Bằng Sông Cửu Long');
INSERT INTO btn.dbo.test_provinces
(old_province, new_province, [zone])
VALUES(N'Thái Nguyên', N'Thái Nguyên', N'Đông Bắc Bộ');

-- dbo.test_containers:
create table dbo.test_containers (
	container_key varchar(255) not null constraint unique_test_container_key default newid(),
	container_size int not null,
	container_status char(1) null,
	container_type char(2) null,
	start_time datetime2 default getdate() not null,
	end_time datetime2 null,
	is_active char(1) default 'y' not null,
	constraint pk_test_containers primary key (container_key)
);

-- dbo.test_services:
create table dbo.test_services (
	service_key varchar(255) not null constraint unique_test_service_key default newid(),
	service_name nvarchar(100) not null,
	container_key varchar(255) not null,
	from_date datetime2 null,
	to_date datetime2 null,
	unit_price int default 0 null,
	tax_rate int default 0 null,
	start_time datetime2 default getdate() not null,
	end_time datetime2 null,
	is_active char(1) default 'y' not null,
	constraint pk_test_services primary key (service_key),
	constraint fk_test_services_containers foreign key (container_key) references dbo.test_containers(container_key)
);

-- dbo.test_lines:
create table dbo.test_lines (
	line_key varchar(255) not null constraint unique_test_line_key default newid(),
	receipt_key varchar(255) not null,
	container_number varchar(11) not null,
	service_key varchar(255) not null,
	quantity int,
	discount int,
	amount int,
	constraint pk_test_lines primary key (line_key),
	constraint fk_test_lines_receipts foreign key (receipt_key) references dbo.test_receipts (receipt_key),
	constraint fk_test_lines_services foreign key (service_key) references dbo.test_services (service_key)
);
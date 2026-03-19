-- 高考志愿数据分析平台 - 数据库迁移脚本
-- 创建时间：2026-03-19
-- 说明：创建所有核心数据表

-- 1. 高校信息表（如果不存在）
CREATE TABLE IF NOT EXISTS edu_school (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL COMMENT '高校名称',
    code VARCHAR(50) NOT NULL COMMENT '学校代码',
    province VARCHAR(20) NOT NULL COMMENT '所在省份',
    city VARCHAR(20) NOT NULL COMMENT '所在城市',
    type VARCHAR(20) NOT NULL COMMENT '院校类型',
    is_985 BOOLEAN NOT NULL COMMENT '是否 985',
    is_211 BOOLEAN NOT NULL COMMENT '是否 211',
    is_double_first BOOLEAN NOT NULL COMMENT '是否双一流',
    founded_year INT COMMENT '建校时间',
    description TEXT COMMENT '学校简介',
    website VARCHAR(255) COMMENT '官网',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_province (province),
    INDEX idx_type (type),
    INDEX idx_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='高校信息表';

-- 2. 专业信息表
CREATE TABLE IF NOT EXISTS edu_major (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL COMMENT '专业名称',
    code VARCHAR(50) NOT NULL COMMENT '专业代码',
    duration INT NOT NULL COMMENT '学制',
    degree VARCHAR(50) COMMENT '学位类型',
    subjects TEXT COMMENT '选科建议',
    description TEXT NOT NULL COMMENT '专业介绍',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_code (code),
    INDEX idx_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='专业信息表';

-- 3. 高校专业关系表
CREATE TABLE IF NOT EXISTS edu_school_major (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    school_id BIGINT NOT NULL COMMENT '高校 id',
    major_id BIGINT NOT NULL COMMENT '专业 id',
    description TEXT NOT NULL COMMENT '专业介绍',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (school_id) REFERENCES edu_school(id) ON DELETE CASCADE,
    FOREIGN KEY (major_id) REFERENCES edu_major(id) ON DELETE CASCADE,
    UNIQUE KEY uk_school_major (school_id, major_id),
    INDEX idx_school (school_id),
    INDEX idx_major (major_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='高校专业关系表';

-- 4. 招生录取数据表
CREATE TABLE IF NOT EXISTS edu_adm_record (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    school_id BIGINT NOT NULL COMMENT '高校 id',
    major_id BIGINT NOT NULL COMMENT '专业 id',
    province VARCHAR(50) NOT NULL COMMENT '招生省份',
    year INT NOT NULL COMMENT '招生年份',
    plan_count INT NOT NULL COMMENT '招生计划人数',
    subject VARCHAR(50) NOT NULL COMMENT '选科大类',
    batch VARCHAR(50) NOT NULL COMMENT '招生批次',
    major_group VARCHAR(20) NOT NULL COMMENT '专业组',
    min_score INT NOT NULL COMMENT '最低分',
    min_rank INT NOT NULL COMMENT '最低位次',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (school_id) REFERENCES edu_school(id) ON DELETE CASCADE,
    FOREIGN KEY (major_id) REFERENCES edu_major(id) ON DELETE CASCADE,
    INDEX idx_school_year (school_id, year),
    INDEX idx_province_year (province, year),
    INDEX idx_score (min_score)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='招生录取数据表';

-- 5. 高校热度统计表
CREATE TABLE IF NOT EXISTS ana_school_heat (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    school_id BIGINT NOT NULL COMMENT '高校 id',
    search_count INT NOT NULL COMMENT '搜索次数',
    favorite_count INT NOT NULL COMMENT '收藏次数',
    view_count INT NOT NULL COMMENT '浏览次数',
    heat_score DECIMAL(10,2) NOT NULL COMMENT '热度指数',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (school_id) REFERENCES edu_school(id) ON DELETE CASCADE,
    INDEX idx_heat_score (heat_score DESC),
    INDEX idx_school (school_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='高校热度统计表';

-- 6. 专业就业数据表
CREATE TABLE IF NOT EXISTS ana_major_employment (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    major_id BIGINT NOT NULL COMMENT '专业 id',
    year INT NOT NULL COMMENT '年份',
    avg_salary INT COMMENT '平均薪资',
    industry_distribution TEXT COMMENT '行业分布',
    post_distribution TEXT COMMENT '岗位分布',
    region_distribution TEXT COMMENT '就业地区分布',
    prospect TEXT COMMENT '专业前景',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (major_id) REFERENCES edu_major(id) ON DELETE CASCADE,
    INDEX idx_major_year (major_id, year),
    INDEX idx_salary (avg_salary)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='专业就业数据表';

-- 7. 用户表
CREATE TABLE IF NOT EXISTS usr_user (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL COMMENT '用户名',
    password VARCHAR(255) NOT NULL COMMENT '密码',
    nickname VARCHAR(100) NOT NULL COMMENT '昵称',
    phone VARCHAR(20) COMMENT '手机号',
    email VARCHAR(100) COMMENT '邮箱',
    role VARCHAR(50) NOT NULL COMMENT '用户角色',
    register_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
    status INT NOT NULL DEFAULT 0 COMMENT '状态 0:正常 1:冻结',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY uk_username (username),
    UNIQUE KEY uk_phone (phone),
    UNIQUE KEY uk_email (email),
    INDEX idx_role (role),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 8. 用户收藏表
CREATE TABLE IF NOT EXISTS usr_favorite (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL COMMENT '用户 id',
    favorite_type VARCHAR(50) NOT NULL COMMENT '收藏类型',
    target_id BIGINT NOT NULL COMMENT '收藏对象 id',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '收藏时间',
    FOREIGN KEY (user_id) REFERENCES usr_user(id) ON DELETE CASCADE,
    INDEX idx_user (user_id),
    INDEX idx_type_target (favorite_type, target_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户收藏表';

-- 9. 数据源表
CREATE TABLE IF NOT EXISTS sys_data_source (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    source_name VARCHAR(200) NOT NULL COMMENT '数据源名称',
    source_type VARCHAR(50) NOT NULL COMMENT '数据源类型',
    api_url VARCHAR(255) NOT NULL COMMENT 'API 地址',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_type (source_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='数据源表';

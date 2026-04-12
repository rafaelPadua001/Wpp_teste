--
-- PostgreSQL database dump
--

\restrict xNLTWcGVnjDLuzCq0BKOvbAbgeBnUcUDxfFT3Yy3X3u05po6EFYFSBY3OMLJAKT

-- Dumped from database version 17.6
-- Dumped by pg_dump version 17.6

-- Started on 2026-04-09 14:19:56

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 4976 (class 1262 OID 213806)
-- Name: wpp-db; Type: DATABASE; Schema: -; Owner: -
--

CREATE DATABASE "wpp-db" WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'br';


\unrestrict xNLTWcGVnjDLuzCq0BKOvbAbgeBnUcUDxfFT3Yy3X3u05po6EFYFSBY3OMLJAKT
\encoding SQL_ASCII
\connect -reuse-previous=on "dbname='wpp-db'"
\restrict xNLTWcGVnjDLuzCq0BKOvbAbgeBnUcUDxfFT3Yy3X3u05po6EFYFSBY3OMLJAKT

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 217 (class 1259 OID 213807)
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- TOC entry 223 (class 1259 OID 213848)
-- Name: contacts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.contacts (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    owner_user_id integer NOT NULL,
    name character varying(120) NOT NULL,
    phone character varying(30) NOT NULL,
    email character varying(255),
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- TOC entry 222 (class 1259 OID 213847)
-- Name: contacts_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.contacts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 4977 (class 0 OID 0)
-- Dependencies: 222
-- Name: contacts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.contacts_id_seq OWNED BY public.contacts.id;


--
-- TOC entry 225 (class 1259 OID 213869)
-- Name: messages; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.messages (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    user_id integer,
    contact_id integer,
    phone character varying(30) NOT NULL,
    content text NOT NULL,
    status character varying(30) DEFAULT 'queued'::character varying NOT NULL,
    provider_message_id character varying(120),
    error_message text,
    sent_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- TOC entry 224 (class 1259 OID 213868)
-- Name: messages_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.messages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 4978 (class 0 OID 0)
-- Dependencies: 224
-- Name: messages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.messages_id_seq OWNED BY public.messages.id;


--
-- TOC entry 227 (class 1259 OID 213896)
-- Name: refresh_tokens; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.refresh_tokens (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    user_id integer NOT NULL,
    token character varying(255) NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    revoked_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- TOC entry 226 (class 1259 OID 213895)
-- Name: refresh_tokens_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.refresh_tokens_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 4979 (class 0 OID 0)
-- Dependencies: 226
-- Name: refresh_tokens_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.refresh_tokens_id_seq OWNED BY public.refresh_tokens.id;


--
-- TOC entry 219 (class 1259 OID 213813)
-- Name: tenants; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tenants (
    id integer NOT NULL,
    name character varying(150) NOT NULL,
    plan character varying(50) DEFAULT 'basic'::character varying NOT NULL,
    message_limit integer DEFAULT 1000 NOT NULL,
    messages_used integer DEFAULT 0 NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- TOC entry 218 (class 1259 OID 213812)
-- Name: tenants_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.tenants_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 4980 (class 0 OID 0)
-- Dependencies: 218
-- Name: tenants_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.tenants_id_seq OWNED BY public.tenants.id;


--
-- TOC entry 221 (class 1259 OID 213827)
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id integer NOT NULL,
    tenant_id integer NOT NULL,
    name character varying(120) NOT NULL,
    email character varying(255) NOT NULL,
    password_hash character varying(255) NOT NULL,
    role character varying(20) DEFAULT 'user'::character varying NOT NULL,
    whatsapp character varying(30),
    login_attempts integer DEFAULT 0 NOT NULL,
    blocked_until timestamp with time zone,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    created_by integer
);


--
-- TOC entry 220 (class 1259 OID 213826)
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 4981 (class 0 OID 0)
-- Dependencies: 220
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- TOC entry 4777 (class 2604 OID 213851)
-- Name: contacts id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.contacts ALTER COLUMN id SET DEFAULT nextval('public.contacts_id_seq'::regclass);


--
-- TOC entry 4779 (class 2604 OID 213872)
-- Name: messages id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.messages ALTER COLUMN id SET DEFAULT nextval('public.messages_id_seq'::regclass);


--
-- TOC entry 4782 (class 2604 OID 213899)
-- Name: refresh_tokens id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.refresh_tokens ALTER COLUMN id SET DEFAULT nextval('public.refresh_tokens_id_seq'::regclass);


--
-- TOC entry 4766 (class 2604 OID 213816)
-- Name: tenants id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tenants ALTER COLUMN id SET DEFAULT nextval('public.tenants_id_seq'::regclass);


--
-- TOC entry 4772 (class 2604 OID 213830)
-- Name: users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- TOC entry 4960 (class 0 OID 213807)
-- Dependencies: 217
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.alembic_version VALUES ('0002_add_user_created_by');


--
-- TOC entry 4966 (class 0 OID 213848)
-- Dependencies: 223
-- Data for Name: contacts; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.contacts VALUES (2, 2, 2, 'Rafael', '61991865680', 'rafael.f.p.faria@hotmail.com', NULL, '2026-04-08 22:23:23.553513-03');
INSERT INTO public.contacts VALUES (3, 2, 2, 'maria', '6135431012', 'maria@email.com', NULL, '2026-04-09 09:59:43.270077-03');


--
-- TOC entry 4968 (class 0 OID 213869)
-- Dependencies: 225
-- Data for Name: messages; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.messages VALUES (1, 2, 2, NULL, '61991865680', 'Olá meu caro cliente bonitão da silva', 'archived', 'mock-5680-6190', NULL, '2026-04-08 14:03:38.292842-03', '2026-04-08 14:03:38.28855-03');
INSERT INTO public.messages VALUES (2, 2, 2, NULL, '61991865680', 'Olá meu caro cliente bonitão da silva', 'archived', 'mock-5680-6190', NULL, '2026-04-08 14:04:01.197585-03', '2026-04-08 14:04:01.194839-03');
INSERT INTO public.messages VALUES (3, 2, 2, NULL, '61991865680', 'Olá meu caro cliente bonitão da silva', 'archived', 'mock-5680-6190', NULL, '2026-04-08 14:04:06.22655-03', '2026-04-08 14:04:06.224268-03');
INSERT INTO public.messages VALUES (4, 2, 2, NULL, '61991865680', 'Olá meu caro cliente bonitão da silva', 'archived', 'mock-5680-6190', NULL, '2026-04-08 14:19:35.258224-03', '2026-04-08 14:19:35.255114-03');
INSERT INTO public.messages VALUES (5, 2, 2, NULL, '61991865680', 'Olá meu caro cliente bonitão da silva', 'archived', 'mock-5680-6190', NULL, '2026-04-08 14:30:48.744146-03', '2026-04-08 14:30:48.740996-03');
INSERT INTO public.messages VALUES (6, 2, 2, NULL, '61991865680', 'teste', 'archived', NULL, 'WhatsApp authentication failed', NULL, '2026-04-08 14:37:19.907115-03');
INSERT INTO public.messages VALUES (7, 2, 2, NULL, '61991865680', 'teste', 'archived', NULL, 'WhatsApp authentication failed', NULL, '2026-04-08 14:39:01.822658-03');
INSERT INTO public.messages VALUES (8, 2, 2, NULL, '61991865680', 'weqeq', 'archived', NULL, 'WhatsApp authentication failed', NULL, '2026-04-08 15:09:10.244722-03');
INSERT INTO public.messages VALUES (9, 2, 2, NULL, '61991865680', 'weqeq', 'archived', NULL, 'WhatsApp authentication failed', NULL, '2026-04-08 15:14:04.623453-03');
INSERT INTO public.messages VALUES (10, 2, 2, NULL, '61991865680', 'weqeq', 'archived', NULL, 'WhatsApp authentication failed', NULL, '2026-04-08 15:16:47.715301-03');
INSERT INTO public.messages VALUES (11, 2, 2, NULL, '61991865680', 'weqeq', 'archived', NULL, 'WhatsApp authentication failed', NULL, '2026-04-08 15:17:41.34604-03');
INSERT INTO public.messages VALUES (12, 2, 2, NULL, '61991865680', 'weqeq', 'archived', NULL, 'WhatsApp authentication failed', NULL, '2026-04-08 15:24:01.479674-03');
INSERT INTO public.messages VALUES (13, 2, 2, NULL, '61991865680', 'gfhgfjhf', 'archived', NULL, 'WhatsApp authentication failed', NULL, '2026-04-08 15:24:26.522003-03');
INSERT INTO public.messages VALUES (14, 2, 2, NULL, '61991865680', 'gfhgfjhf', 'archived', NULL, 'WhatsApp authentication failed', NULL, '2026-04-08 16:08:40.834968-03');
INSERT INTO public.messages VALUES (15, 2, 2, 2, '61991865680', 'sadsadasdas', 'archived', NULL, 'WhatsApp authentication failed', NULL, '2026-04-08 22:48:25.130211-03');
INSERT INTO public.messages VALUES (16, 2, 2, 3, '6135431012', 'teste de envio de mensagem', 'archived', NULL, 'WhatsApp authentication failed', NULL, '2026-04-09 10:00:09.428481-03');
INSERT INTO public.messages VALUES (17, 2, 2, 2, '61991865680', 'teste de envio de mensagem', 'archived', NULL, 'WhatsApp authentication failed', NULL, '2026-04-09 10:00:09.428481-03');


--
-- TOC entry 4970 (class 0 OID 213896)
-- Dependencies: 227
-- Data for Name: refresh_tokens; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.refresh_tokens VALUES (1, 2, 2, 'YrGjpMXg2bYs8jlLvAb8Tb7YhoZ88tVQWxSbCFzpLDeP0uTB6ObLtZOhui4u6tXQ', '2026-04-15 14:02:46.124036-03', NULL, '2026-04-08 14:02:46.123125-03');
INSERT INTO public.refresh_tokens VALUES (2, 2, 2, 'FHloWfBqcm-93U-tfyZTdYlEa5ICBVSJpE2McQRk3EYNCYdTTW3ytqJ1y1JQ2QV2', '2026-04-15 14:37:13.041472-03', NULL, '2026-04-08 14:37:13.0362-03');
INSERT INTO public.refresh_tokens VALUES (3, 2, 2, 'XGMETZs7GnZuxkLaq2kdqDmrako4PDiG95Q4gQi5a14JUK2n07SJUH87CorKhrnP', '2026-04-15 15:09:05.712998-03', NULL, '2026-04-08 15:09:05.708023-03');
INSERT INTO public.refresh_tokens VALUES (4, 2, 2, '9OKE73tzdWlErykGMJAaAF3SSK6GxfJnsz-1l4W3JMbOc9cNRtnMikPdOtD0l-tT', '2026-04-15 15:24:18.807092-03', NULL, '2026-04-08 15:24:18.806265-03');
INSERT INTO public.refresh_tokens VALUES (5, 2, 2, 'leDC23sFnd42zgxb4jjOs_nCiUdLaFJk2DQwkdu7uQOV4Y6bn1Pd2uF5UY90Y6aC', '2026-04-15 16:08:39.302009-03', NULL, '2026-04-08 16:08:39.296788-03');
INSERT INTO public.refresh_tokens VALUES (6, 2, 2, 'pNximGCEb_xbOOtLVkf_R9MWxB4lBGVzyRlWR6ZP-7dJi83wWGtbYm3GyCtzG8B3', '2026-04-15 22:20:42.525411-03', NULL, '2026-04-08 22:20:42.515608-03');
INSERT INTO public.refresh_tokens VALUES (7, 2, 2, 'j1KW1qjZ5odVTuubcwD2BIuYA48rxuKBcyv50uffHGRPjfXiV5K-_Zna20GJsvKn', '2026-04-15 22:33:31.569357-03', NULL, '2026-04-08 22:33:31.568223-03');
INSERT INTO public.refresh_tokens VALUES (8, 5, 3, 'oARqBddX4Kpsw56y7dJbla-OYYu3fqOpEioJ3oJFmxsJewzZfbhHtS9gN6fO0GCL', '2026-04-15 22:36:34.66904-03', NULL, '2026-04-08 22:36:34.668294-03');
INSERT INTO public.refresh_tokens VALUES (9, 2, 2, 'tOAjWALGWb6ry3PaffnDYtoJzZFi_Oj8zvFCOJhMOFugeq0gGKPnR1JuvOBESJj1', '2026-04-15 22:44:10.225928-03', NULL, '2026-04-08 22:44:10.219782-03');
INSERT INTO public.refresh_tokens VALUES (10, 5, 4, 'cRHL5pZ1853yaymIaK0Gyus1lZ8b2T2VNYeARAunm17xMDE-lp5GgNs5zkAK5r5s', '2026-04-15 22:44:29.686428-03', NULL, '2026-04-08 22:44:29.685486-03');
INSERT INTO public.refresh_tokens VALUES (11, 2, 2, 'q1bgyZyS28D5KIseJWDL-kf1LjRk--ad_nF-Ayu825jF1eYKcp7LrZn8SzFKm8Xq', '2026-04-15 22:44:49.86181-03', NULL, '2026-04-08 22:44:49.861142-03');
INSERT INTO public.refresh_tokens VALUES (12, 5, 3, 'RO5E_R6D4agZXpUm3JwAN4NFOrsjp39AusCNXREfe8Cbvor3waXwZQz19B6HkX_H', '2026-04-15 22:45:10.476882-03', NULL, '2026-04-08 22:45:10.476181-03');
INSERT INTO public.refresh_tokens VALUES (13, 2, 2, 'Mxr6QytlrwK3FRjaaT-9JKhs76zKQcfbkO2Z3Yn5yclc5rx2ivHlAGREzBmpP11m', '2026-04-15 22:47:49.792795-03', NULL, '2026-04-08 22:47:49.792075-03');
INSERT INTO public.refresh_tokens VALUES (14, 5, 4, 'DcF93ua1de3gpxLIJQejRVGLbRba8KLkDN3meDnsClN2xezA8RLX25ndNNrz-XAN', '2026-04-15 22:53:57.444144-03', NULL, '2026-04-08 22:53:57.443543-03');
INSERT INTO public.refresh_tokens VALUES (15, 5, 4, 'H_1RZPs43mSGcJy7OPkA8H4FYG-3EODbIuLJzzZirQ_XSQ6-Ns5IoFekth-cV82R', '2026-04-16 09:58:55.416778-03', NULL, '2026-04-09 09:58:55.407024-03');
INSERT INTO public.refresh_tokens VALUES (16, 2, 2, 'RrplVd1yOcbEy9g-pSTiVA2L4lkTeWJM1g-CJwVSLzpALHThAX-MyTjFzJo31D0B', '2026-04-16 09:59:17.524606-03', NULL, '2026-04-09 09:59:17.524004-03');
INSERT INTO public.refresh_tokens VALUES (17, 2, 2, 'fgSTba60x_G7AKo-2vTeM-uU1bDRxCroWkMj2aFgrGcopZgt5H3qrwYf5VSCc7t8', '2026-04-16 11:24:32.635865-03', NULL, '2026-04-09 11:24:32.619441-03');
INSERT INTO public.refresh_tokens VALUES (18, 5, 4, 'T3_fFxvDeSWxMhrddMWwwUpwf6okCNEjJh-eEDVqaJ7m2ip4foY3-690DGWOfKmE', '2026-04-16 11:59:19.194345-03', NULL, '2026-04-09 11:59:19.192563-03');


--
-- TOC entry 4962 (class 0 OID 213813)
-- Dependencies: 219
-- Data for Name: tenants; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.tenants VALUES (1, 'Clinica Alpha', 'basic', 1000, 0, true, '2026-04-08 13:51:54.436687-03');
INSERT INTO public.tenants VALUES (2, 'Teste', 'basic', 1000, 5, true, '2026-04-08 14:01:48.030382-03');
INSERT INTO public.tenants VALUES (5, 'Clinica Alphaaaa', 'basic', 1000, 0, true, '2026-04-08 22:36:02.090347-03');


--
-- TOC entry 4964 (class 0 OID 213827)
-- Dependencies: 221
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.users VALUES (1, 1, 'Rafael', 'rafael@alpha.com', '$pbkdf2-sha256$29000$lzIm5Lz3HiMkhDDmPCeEUA$aqrl07hihQ8nA3Hkpw2aY26.W7WBIli5j5p3PiKwGKk', 'admin', '556199999999', 0, NULL, true, '2026-04-08 13:51:54.436687-03', NULL);
INSERT INTO public.users VALUES (2, 2, 'Teste da silva', 'teste@email.com', '$pbkdf2-sha256$29000$SOl9T8kZI8QY49y7V8q5Nw$N6IiZoXDGv6QaE2eQAgiMIxyjxh3QHsviV5oyMvFcV4', 'admin', NULL, 0, NULL, true, '2026-04-08 14:01:48.030382-03', NULL);
INSERT INTO public.users VALUES (3, 5, 'Rafael', 'rafael.f.p.faria@hotmail.com', '$pbkdf2-sha256$29000$GyPkPCeEUEopRciZE6K0Fg$yJ/e3QYEpY.4GXpqpC.GkrZfRHrL6K3gJ29Ngz4vllI', 'admin', '1234567890994231', 0, NULL, true, '2026-04-08 22:36:02.090347-03', NULL);
INSERT INTO public.users VALUES (4, 5, 'joao', 'joao@email.com', '$pbkdf2-sha256$29000$htAawzhHKIXQ.t/b.z.nVA$KwaDgHbUBJm3KLNOSCoIbE6mRHdnoL/ej51n6P1YYp4', 'user', '6145678912345', 0, NULL, true, '2026-04-08 22:40:09.026289-03', NULL);
INSERT INTO public.users VALUES (5, 2, 'Novo user', 'NovoUser@email.com', '$pbkdf2-sha256$29000$0pqztrbWWqu1Nua8N4awVg$6JgAEj4z6gi30vBNdQ81TBu5dwMBtHZEOdwWVxyEqpo', 'user', '6191565656', 0, NULL, true, '2026-04-09 10:00:48.522039-03', 2);


--
-- TOC entry 4982 (class 0 OID 0)
-- Dependencies: 222
-- Name: contacts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.contacts_id_seq', 3, true);


--
-- TOC entry 4983 (class 0 OID 0)
-- Dependencies: 224
-- Name: messages_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.messages_id_seq', 17, true);


--
-- TOC entry 4984 (class 0 OID 0)
-- Dependencies: 226
-- Name: refresh_tokens_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.refresh_tokens_id_seq', 18, true);


--
-- TOC entry 4985 (class 0 OID 0)
-- Dependencies: 218
-- Name: tenants_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.tenants_id_seq', 5, true);


--
-- TOC entry 4986 (class 0 OID 0)
-- Dependencies: 220
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.users_id_seq', 5, true);


--
-- TOC entry 4785 (class 2606 OID 213811)
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- TOC entry 4796 (class 2606 OID 213856)
-- Name: contacts contacts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.contacts
    ADD CONSTRAINT contacts_pkey PRIMARY KEY (id);


--
-- TOC entry 4800 (class 2606 OID 213878)
-- Name: messages messages_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_pkey PRIMARY KEY (id);


--
-- TOC entry 4803 (class 2606 OID 213902)
-- Name: refresh_tokens refresh_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.refresh_tokens
    ADD CONSTRAINT refresh_tokens_pkey PRIMARY KEY (id);


--
-- TOC entry 4805 (class 2606 OID 213904)
-- Name: refresh_tokens refresh_tokens_token_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.refresh_tokens
    ADD CONSTRAINT refresh_tokens_token_key UNIQUE (token);


--
-- TOC entry 4787 (class 2606 OID 213825)
-- Name: tenants tenants_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tenants
    ADD CONSTRAINT tenants_name_key UNIQUE (name);


--
-- TOC entry 4789 (class 2606 OID 213823)
-- Name: tenants tenants_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tenants
    ADD CONSTRAINT tenants_pkey PRIMARY KEY (id);


--
-- TOC entry 4792 (class 2606 OID 213840)
-- Name: users uq_users_tenant_email; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT uq_users_tenant_email UNIQUE (tenant_id, email);


--
-- TOC entry 4794 (class 2606 OID 213838)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- TOC entry 4797 (class 1259 OID 213867)
-- Name: ix_contacts_tenant_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_contacts_tenant_id ON public.contacts USING btree (tenant_id);


--
-- TOC entry 4798 (class 1259 OID 213894)
-- Name: ix_messages_tenant_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_messages_tenant_id ON public.messages USING btree (tenant_id);


--
-- TOC entry 4801 (class 1259 OID 213915)
-- Name: ix_refresh_tokens_tenant_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_refresh_tokens_tenant_id ON public.refresh_tokens USING btree (tenant_id);


--
-- TOC entry 4790 (class 1259 OID 213846)
-- Name: ix_users_tenant_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_users_tenant_id ON public.users USING btree (tenant_id);


--
-- TOC entry 4808 (class 2606 OID 213862)
-- Name: contacts contacts_owner_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.contacts
    ADD CONSTRAINT contacts_owner_user_id_fkey FOREIGN KEY (owner_user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- TOC entry 4809 (class 2606 OID 213857)
-- Name: contacts contacts_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.contacts
    ADD CONSTRAINT contacts_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id) ON DELETE CASCADE;


--
-- TOC entry 4806 (class 2606 OID 213916)
-- Name: users fk_users_created_by_users; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT fk_users_created_by_users FOREIGN KEY (created_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- TOC entry 4810 (class 2606 OID 213889)
-- Name: messages messages_contact_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_contact_id_fkey FOREIGN KEY (contact_id) REFERENCES public.contacts(id) ON DELETE SET NULL;


--
-- TOC entry 4811 (class 2606 OID 213879)
-- Name: messages messages_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id) ON DELETE CASCADE;


--
-- TOC entry 4812 (class 2606 OID 213884)
-- Name: messages messages_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- TOC entry 4813 (class 2606 OID 213905)
-- Name: refresh_tokens refresh_tokens_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.refresh_tokens
    ADD CONSTRAINT refresh_tokens_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id) ON DELETE CASCADE;


--
-- TOC entry 4814 (class 2606 OID 213910)
-- Name: refresh_tokens refresh_tokens_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.refresh_tokens
    ADD CONSTRAINT refresh_tokens_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- TOC entry 4807 (class 2606 OID 213841)
-- Name: users users_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id) ON DELETE CASCADE;


-- Completed on 2026-04-09 14:19:57

--
-- PostgreSQL database dump complete
--

\unrestrict xNLTWcGVnjDLuzCq0BKOvbAbgeBnUcUDxfFT3Yy3X3u05po6EFYFSBY3OMLJAKT


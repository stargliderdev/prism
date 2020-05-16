

INSERT INTO public.software_lic_status (lic_st_id, lic_st_name) VALUES (4, 'Actualizada');
INSERT INTO public.software_lic_status (lic_st_id, lic_st_name) VALUES (3, 'Em Actualização');


alter table software_lic_status rename column sls_id to lic_st_id;
alter table software_lic_status rename column sls_name to lic_st_name;
alter table software_lic_status alter column lic_st_name type varchar(20) using lic_st_name::varchar(20);

update software set sf_status =4
where sf_id <4796

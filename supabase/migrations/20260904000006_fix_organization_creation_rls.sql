-- ==============================================================================
-- Migration: 20260904000006_fix_organization_creation_rls.sql
-- Description: Función RPC atómica SECURITY DEFINER para crear organizaciones y asignar propietario
-- ==============================================================================

-- 1. Función RPC para crear una organización y asignar al usuario actual como agency_owner atómicamente
CREATE OR REPLACE FUNCTION public.create_organization_with_owner(
    p_name TEXT,
    p_slug TEXT,
    p_plan TEXT DEFAULT 'standard',
    p_logo_url TEXT DEFAULT NULL
)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_user_id UUID;
    v_org public.organizations%ROWTYPE;
    v_clean_slug TEXT;
BEGIN
    -- Validar autenticación
    v_user_id := auth.uid();
    IF v_user_id IS NULL THEN
        RAISE EXCEPTION 'Usuario no autenticado para crear una organización';
    END IF;

    -- Formatear slug
    v_clean_slug := lower(regexp_replace(p_slug, '[^a-zA-Z0-9-]', '-', 'g'));
    IF v_clean_slug = '' OR v_clean_slug IS NULL THEN
        v_clean_slug := 'org-' || substr(md5(random()::text), 1, 8);
    END IF;

    -- 1. Crear organización
    INSERT INTO public.organizations (name, slug, plan, logo_url)
    VALUES (
        p_name,
        v_clean_slug,
        COALESCE(p_plan, 'standard'),
        p_logo_url
    )
    RETURNING * INTO v_org;

    -- 2. Asignar al creador como agency_owner
    INSERT INTO public.organization_members (organization_id, user_id, role)
    VALUES (
        v_org.id,
        v_user_id,
        'agency_owner'
    );

    RETURN to_jsonb(v_org);
END;
$$;

-- 2. Otorgar permisos de ejecución a usuarios autenticados
GRANT EXECUTE ON FUNCTION public.create_organization_with_owner(TEXT, TEXT, TEXT, TEXT) TO authenticated;

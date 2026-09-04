-- ==============================================================================
-- Migration: 20260904000004_rls_security_policies.sql
-- Description: Políticas de Seguridad a Nivel de Fila (RLS) y funciones de contexto
-- ==============================================================================

-- 1. Funciones auxiliares de seguridad (SECURITY DEFINER para consultar membresías)

CREATE OR REPLACE FUNCTION public.get_user_org_ids()
RETURNS SETOF UUID AS $$
    SELECT organization_id 
    FROM public.organization_members 
    WHERE user_id = auth.uid();
$$ LANGUAGE sql STABLE SECURITY DEFINER;

CREATE OR REPLACE FUNCTION public.is_org_member(check_org_id UUID)
RETURNS BOOLEAN AS $$
    SELECT EXISTS (
        SELECT 1 
        FROM public.organization_members 
        WHERE organization_id = check_org_id 
          AND user_id = auth.uid()
    );
$$ LANGUAGE sql STABLE SECURITY DEFINER;

CREATE OR REPLACE FUNCTION public.is_org_admin(check_org_id UUID)
RETURNS BOOLEAN AS $$
    SELECT EXISTS (
        SELECT 1 
        FROM public.organization_members 
        WHERE organization_id = check_org_id 
          AND user_id = auth.uid()
          AND role IN ('agency_owner', 'manager')
    );
$$ LANGUAGE sql STABLE SECURITY DEFINER;

CREATE OR REPLACE FUNCTION public.get_user_creator_ids(check_org_id UUID)
RETURNS SETOF UUID AS $$
    SELECT id 
    FROM public.creators 
    WHERE organization_id = check_org_id 
      AND user_id = auth.uid();
$$ LANGUAGE sql STABLE SECURITY DEFINER;

-- 2. Habilitar RLS en todas las tablas públicas
ALTER TABLE public.organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.organization_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.creators ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.channels ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.import_batches ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.streaming_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.channel_alerts ENABLE ROW LEVEL SECURITY;

-- 3. Políticas para `profiles`
CREATE POLICY "Users can view their own profile"
    ON public.profiles FOR SELECT
    USING (id = auth.uid());

CREATE POLICY "Users can update their own profile"
    ON public.profiles FOR UPDATE
    USING (id = auth.uid());

CREATE POLICY "Organization members can view peer profiles"
    ON public.profiles FOR SELECT
    USING (
        id IN (
            SELECT user_id 
            FROM public.organization_members 
            WHERE organization_id IN (SELECT public.get_user_org_ids())
        )
    );

-- 4. Políticas para `organizations`
CREATE POLICY "Members can view their organizations"
    ON public.organizations FOR SELECT
    USING (id IN (SELECT public.get_user_org_ids()));

CREATE POLICY "Owners can update their organization"
    ON public.organizations FOR UPDATE
    USING (public.is_org_admin(id));

CREATE POLICY "Authenticated users can create an organization"
    ON public.organizations FOR INSERT
    WITH CHECK (auth.role() = 'authenticated');

-- 5. Políticas para `organization_members`
CREATE POLICY "Members can view roster of their organizations"
    ON public.organization_members FOR SELECT
    USING (organization_id IN (SELECT public.get_user_org_ids()));

CREATE POLICY "Admins can manage members in their organization"
    ON public.organization_members FOR ALL
    USING (public.is_org_admin(organization_id));

-- 6. Políticas para `creators`
CREATE POLICY "Managers and owners can view all creators in org"
    ON public.creators FOR SELECT
    USING (
        public.is_org_admin(organization_id)
        OR user_id = auth.uid()
    );

CREATE POLICY "Admins can manage creators in org"
    ON public.creators FOR ALL
    USING (public.is_org_admin(organization_id));

-- 7. Políticas para `channels`
CREATE POLICY "Members can view channels in their org"
    ON public.channels FOR SELECT
    USING (
        creator_id IN (
            SELECT id FROM public.creators 
            WHERE organization_id IN (SELECT public.get_user_org_ids())
        )
    );

CREATE POLICY "Admins can manage channels"
    ON public.channels FOR ALL
    USING (
        creator_id IN (
            SELECT id FROM public.creators 
            WHERE public.is_org_admin(organization_id)
        )
    );

-- 8. Políticas para `import_batches`
CREATE POLICY "Members can view import batches in org"
    ON public.import_batches FOR SELECT
    USING (organization_id IN (SELECT public.get_user_org_ids()));

CREATE POLICY "Admins can create import batches"
    ON public.import_batches FOR INSERT
    WITH CHECK (public.is_org_admin(organization_id));

-- 9. Políticas para `streaming_sessions`
CREATE POLICY "Managers can view all sessions in org, Creators only their own"
    ON public.streaming_sessions FOR SELECT
    USING (
        public.is_org_admin(organization_id)
        OR creator_id IN (SELECT public.get_user_creator_ids(organization_id))
    );

CREATE POLICY "Admins can insert and manage streaming sessions"
    ON public.streaming_sessions FOR ALL
    USING (public.is_org_admin(organization_id));

-- 10. Políticas para `channel_alerts`
CREATE POLICY "Managers can view all alerts, Creators only their own"
    ON public.channel_alerts FOR SELECT
    USING (
        public.is_org_admin(organization_id)
        OR creator_id IN (SELECT public.get_user_creator_ids(organization_id))
    );

CREATE POLICY "Admins can manage alerts"
    ON public.channel_alerts FOR ALL
    USING (public.is_org_admin(organization_id));

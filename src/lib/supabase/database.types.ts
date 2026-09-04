export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[];

export type MemberRole = 'agency_owner' | 'manager' | 'creator' | 'analyst';
export type CreatorStatus = 'active' | 'inactive' | 'suspended';
export type PlatformType = 'twitch' | 'youtube' | 'kick' | 'tiktok';
export type AlertSeverity = 'info' | 'warning' | 'critical';
export type AlertStatus = 'active' | 'resolved' | 'appealed';
export type ImportStatus = 'processing' | 'completed' | 'failed';

export type Database = {
  public: {
    Tables: {
      organizations: {
        Row: {
          id: string;
          name: string;
          slug: string;
          logo_url: string | null;
          plan: string;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          name: string;
          slug: string;
          logo_url?: string | null;
          plan?: string;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          name?: string;
          slug?: string;
          logo_url?: string | null;
          plan?: string;
          created_at?: string;
          updated_at?: string;
        };
        Relationships: [];
      };
      profiles: {
        Row: {
          id: string;
          email: string;
          full_name: string | null;
          avatar_url: string | null;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id: string;
          email: string;
          full_name?: string | null;
          avatar_url?: string | null;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          email?: string;
          full_name?: string | null;
          avatar_url?: string | null;
          created_at?: string;
          updated_at?: string;
        };
        Relationships: [];
      };
      organization_members: {
        Row: {
          id: string;
          organization_id: string;
          user_id: string;
          role: MemberRole;
          created_at: string;
        };
        Insert: {
          id?: string;
          organization_id: string;
          user_id: string;
          role?: MemberRole;
          created_at?: string;
        };
        Update: {
          id?: string;
          organization_id?: string;
          user_id?: string;
          role?: MemberRole;
          created_at?: string;
        };
        Relationships: [];
      };
      creators: {
        Row: {
          id: string;
          organization_id: string;
          user_id: string | null;
          display_name: string;
          handle: string;
          avatar_url: string | null;
          bio: string | null;
          primary_platform: PlatformType;
          status: CreatorStatus;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          organization_id: string;
          user_id?: string | null;
          display_name: string;
          handle: string;
          avatar_url?: string | null;
          bio?: string | null;
          primary_platform?: PlatformType;
          status?: CreatorStatus;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          organization_id?: string;
          user_id?: string | null;
          display_name?: string;
          handle?: string;
          avatar_url?: string | null;
          bio?: string | null;
          primary_platform?: PlatformType;
          status?: CreatorStatus;
          created_at?: string;
          updated_at?: string;
        };
        Relationships: [];
      };
      channels: {
        Row: {
          id: string;
          creator_id: string;
          platform: PlatformType;
          platform_channel_id: string;
          channel_url: string | null;
          followers_count: number;
          subscribers_count: number;
          is_live: boolean;
          last_synced_at: string | null;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          creator_id: string;
          platform: PlatformType;
          platform_channel_id: string;
          channel_url?: string | null;
          followers_count?: number;
          subscribers_count?: number;
          is_live?: boolean;
          last_synced_at?: string | null;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          creator_id?: string;
          platform?: PlatformType;
          platform_channel_id?: string;
          channel_url?: string | null;
          followers_count?: number;
          subscribers_count?: number;
          is_live?: boolean;
          last_synced_at?: string | null;
          created_at?: string;
          updated_at?: string;
        };
        Relationships: [];
      };
      streaming_sessions: {
        Row: {
          id: string;
          organization_id: string;
          creator_id: string;
          channel_id: string | null;
          import_batch_id: string | null;
          session_title: string;
          game_or_category: string | null;
          platform: PlatformType;
          streamed_at: string;
          duration_seconds: number;
          hours_streamed: number;
          peak_viewers: number;
          avg_ccv: number;
          chat_messages_count: number;
          new_followers: number;
          ad_revenue: number;
          donations_revenue: number;
          subs_revenue: number;
          total_earnings: number;
          earnings_per_hour: number;
          created_at: string;
        };
        Insert: {
          id?: string;
          organization_id: string;
          creator_id: string;
          channel_id?: string | null;
          import_batch_id?: string | null;
          session_title?: string;
          game_or_category?: string | null;
          platform?: PlatformType;
          streamed_at: string;
          duration_seconds?: number;
          peak_viewers?: number;
          avg_ccv?: number;
          chat_messages_count?: number;
          new_followers?: number;
          ad_revenue?: number;
          donations_revenue?: number;
          subs_revenue?: number;
          total_earnings?: number;
          earnings_per_hour?: number;
          created_at?: string;
        };
        Update: {
          id?: string;
          organization_id?: string;
          creator_id?: string;
          channel_id?: string | null;
          import_batch_id?: string | null;
          session_title?: string;
          game_or_category?: string | null;
          platform?: PlatformType;
          streamed_at?: string;
          duration_seconds?: number;
          peak_viewers?: number;
          avg_ccv?: number;
          chat_messages_count?: number;
          new_followers?: number;
          ad_revenue?: number;
          donations_revenue?: number;
          subs_revenue?: number;
          total_earnings?: number;
          earnings_per_hour?: number;
          created_at?: string;
        };
        Relationships: [];
      };
      published_videos: {
        Row: {
          id: string;
          organization_id: string;
          creator_id: string;
          channel_id: string | null;
          import_batch_id: string | null;
          title: string;
          platform: PlatformType;
          video_url: string | null;
          thumbnail_url: string | null;
          published_at: string;
          duration_seconds: number;
          views_count: number;
          likes_count: number;
          comments_count: number;
          shares_count: number;
          estimated_revenue: number;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          organization_id: string;
          creator_id: string;
          channel_id?: string | null;
          import_batch_id?: string | null;
          title: string;
          platform?: PlatformType;
          video_url?: string | null;
          thumbnail_url?: string | null;
          published_at?: string;
          duration_seconds?: number;
          views_count?: number;
          likes_count?: number;
          comments_count?: number;
          shares_count?: number;
          estimated_revenue?: number;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          organization_id?: string;
          creator_id?: string;
          channel_id?: string | null;
          import_batch_id?: string | null;
          title?: string;
          platform?: PlatformType;
          video_url?: string | null;
          thumbnail_url?: string | null;
          published_at?: string;
          duration_seconds?: number;
          views_count?: number;
          likes_count?: number;
          comments_count?: number;
          shares_count?: number;
          estimated_revenue?: number;
          created_at?: string;
          updated_at?: string;
        };
        Relationships: [];
      };
      channel_alerts: {
        Row: {
          id: string;
          organization_id: string;
          creator_id: string;
          channel_id: string | null;
          alert_type: string;
          severity: AlertSeverity;
          status: AlertStatus;
          title: string;
          description: string | null;
          occurred_at: string;
          resolved_at: string | null;
          resolution_notes: string | null;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          organization_id: string;
          creator_id: string;
          channel_id?: string | null;
          alert_type: string;
          severity?: AlertSeverity;
          status?: AlertStatus;
          title: string;
          description?: string | null;
          occurred_at?: string;
          resolved_at?: string | null;
          resolution_notes?: string | null;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          organization_id?: string;
          creator_id?: string;
          channel_id?: string | null;
          alert_type?: string;
          severity?: AlertSeverity;
          status?: AlertStatus;
          title?: string;
          description?: string | null;
          occurred_at?: string;
          resolved_at?: string | null;
          resolution_notes?: string | null;
          created_at?: string;
          updated_at?: string;
        };
        Relationships: [];
      };
      import_batches: {
        Row: {
          id: string;
          organization_id: string;
          uploaded_by: string | null;
          filename: string;
          source_platform: PlatformType;
          total_rows: number;
          valid_rows: number;
          error_count: number;
          status: ImportStatus;
          error_summary: Json | null;
          created_at: string;
        };
        Insert: {
          id?: string;
          organization_id: string;
          uploaded_by?: string | null;
          filename: string;
          source_platform?: PlatformType;
          total_rows?: number;
          valid_rows?: number;
          error_count?: number;
          status?: ImportStatus;
          error_summary?: Json | null;
          created_at?: string;
        };
        Update: {
          id?: string;
          organization_id?: string;
          uploaded_by?: string | null;
          filename?: string;
          source_platform?: PlatformType;
          total_rows?: number;
          valid_rows?: number;
          error_count?: number;
          status?: ImportStatus;
          error_summary?: Json | null;
          created_at?: string;
        };
        Relationships: [];
      };
    };
    Views: {
      mv_creator_performance_summary: {
        Row: {
          creator_id: string;
          organization_id: string;
          display_name: string;
          handle: string;
          primary_platform: PlatformType;
          status: CreatorStatus;
          total_streams: number;
          total_stream_seconds: number;
          total_hours_streamed: number;
          overall_avg_ccv: number;
          max_peak_viewers: number;
          total_stream_earnings: number;
          total_videos: number;
          total_video_views: number;
          total_video_likes: number;
          total_video_earnings: number;
          total_combined_revenue: number;
          last_refreshed_at: string;
        };
        Relationships: [];
      };
      mv_platform_category_stats: {
        Row: {
          organization_id: string;
          platform: PlatformType;
          category_name: string;
          session_count: number;
          total_hours: number;
          avg_ccv: number;
          max_peak: number;
          total_revenue: number;
        };
        Relationships: [];
      };
    };
    Functions: {
      create_organization_with_owner: {
        Args: {
          p_name: string;
          p_slug: string;
          p_plan?: string;
          p_logo_url?: string | null;
        };
        Returns: Database['public']['Tables']['organizations']['Row'];
      };
      refresh_creator_analytics_mv: {
        Args: Record<PropertyKey, never>;
        Returns: void;
      };
      get_user_org_ids: {
        Args: Record<PropertyKey, never>;
        Returns: string[];
      };
      is_org_member: {
        Args: { check_org_id: string };
        Returns: boolean;
      };
      is_org_admin: {
        Args: { check_org_id: string };
        Returns: boolean;
      };
      get_user_creator_ids: {
        Args: { check_org_id: string };
        Returns: string[];
      };
    };
    Enums: {
      member_role: MemberRole;
      creator_status: CreatorStatus;
      platform_type: PlatformType;
      alert_severity: AlertSeverity;
      alert_status: AlertStatus;
      import_status: ImportStatus;
    };
    CompositeTypes: Record<string, never>;
  };
};

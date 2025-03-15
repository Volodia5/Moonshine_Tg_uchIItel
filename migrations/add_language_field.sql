-- Add language column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'language'
    ) THEN
        ALTER TABLE public.users ADD COLUMN language text DEFAULT 'ru';
    END IF;
END $$;

-- Update existing users to have Russian as default language
UPDATE public.users SET language = 'ru' WHERE language IS NULL; 
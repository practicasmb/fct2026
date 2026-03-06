import { ChangeDetectionStrategy, Component, signal } from '@angular/core';
import { ButtonComponent, DialogComponent, BadgeComponent, CheckboxComponent } from '@shared/ui';
import type { DialogVariant, DialogSize } from '@shared/ui';

@Component({
  selector: 'app-root',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [ButtonComponent, DialogComponent, BadgeComponent, CheckboxComponent],
  templateUrl: './app.html',
})
export class AppComponent {
  readonly dialogVisible = signal(false);
  readonly dialogVariant = signal<DialogVariant>('default');
  readonly dialogSize    = signal<DialogSize>('default');

  openDialog(variant: DialogVariant, size: DialogSize = 'default'): void {
    this.dialogVariant.set(variant);
    this.dialogSize.set(size);
    this.dialogVisible.set(true);
  }
}

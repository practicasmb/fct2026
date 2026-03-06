import {
  ChangeDetectionStrategy,
  Component,
  input,
  output,
  signal,
  computed,
  effect,
  forwardRef,
} from '@angular/core';
import { ControlValueAccessor, NG_VALUE_ACCESSOR, FormsModule } from '@angular/forms';
import { CheckboxModule } from 'primeng/checkbox';

// PrimeNG checkbox visual variants — 'outlined' is the default
export type CheckboxVariant = 'outlined' | 'filled';

// Maps to PrimeNG size prop
export type CheckboxSize = 'default' | 'sm' | 'lg';

const SIZE_MAP: Record<CheckboxSize, 'small' | 'large' | undefined> = {
  default: undefined,
  sm:      'small',
  lg:      'large',
};

@Component({
  selector: 'ui-checkbox',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [CheckboxModule, FormsModule],
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => CheckboxComponent),
      multi: true,
    },
  ],
  templateUrl: './checkbox.component.html',
})
export class CheckboxComponent implements ControlValueAccessor {
  // ── Inputs ──
  label      = input<string>('');
  // Unique id linking the label [for] to the checkbox [inputId]
  inputId    = input<string>(`ui-checkbox-${Math.random().toString(36).slice(2)}`);
  disabled   = input<boolean>(false);
  invalid    = input<boolean>(false);
  variant    = input<CheckboxVariant>('outlined');
  size       = input<CheckboxSize>('default');
  styleClass = input<string>('');

  // Optional controlled input — useful without a form
  checked       = input<boolean>(false);
  indeterminate = input<boolean>(false);

  // ── Output ──
  valueChange = output<boolean>();

  // ── Internal state ──
  readonly value = signal<boolean>(false);

  // Sync the checked input with the internal signal when used without a form
  constructor() {
    effect(() => this.value.set(this.checked()));
  }

  // ── Computed ──
  resolvedSize = computed(() => SIZE_MAP[this.size()]);

  // ── CVA ──
  private onChange: (val: boolean) => void = () => {};
  onTouched: () => void = () => {};

  writeValue(val: boolean): void {
    this.value.set(val ?? false);
  }

  registerOnChange(fn: (val: boolean) => void): void {
    this.onChange = fn;
  }

  registerOnTouched(fn: () => void): void {
    this.onTouched = fn;
  }

  setDisabledState(): void {
    // Disabled state is handled reactively via the disabled() input
  }

  // ── Handlers ──
  onInput(checked: boolean): void {
    this.value.set(checked);
    this.onChange(checked);
    this.onTouched();
    this.valueChange.emit(checked);
  }
}